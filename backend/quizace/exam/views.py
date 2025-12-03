from collections import OrderedDict
from datetime import timedelta
from random import sample
from typing import Dict, List, Optional, Tuple

from django.db import transaction
from django.db.models import Q, QuerySet, Count
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .constants import OBJECTIVE_SCORE_PER_QUESTION, resolve_score
from .models import ExamAssignment, PracticeAttempt, PracticeAttemptItem, Question, Subject, WrongBookEntry
from .serializers import (
    ExamAssignmentSerializer,
    PracticeAttemptItemSerializer,
    PracticeAttemptSerializer,
    PracticeQuestionSerializer,
    QuestionSerializer,
    SubjectSerializer,
    WrongBookEntrySerializer,
)


QUESTION_DEFAULT_SIZE = {
    "objective": 10,
    "subjective": 5,
}

def get_expire_time(attempt: PracticeAttempt):
    return attempt.started_at + timedelta(seconds=attempt.duration_seconds)


def get_remaining_seconds(attempt: PracticeAttempt):
    expire_time = get_expire_time(attempt)
    remaining = int((expire_time - timezone.now()).total_seconds())
    return expire_time, max(0, remaining)


def build_questions(subject: Subject, question_type: str, size: int) -> Tuple[List[Question], int]:
    questions_qs: QuerySet[Question] = Question.objects.filter(
        subject=subject,
        question_type=question_type,
    )
    total = questions_qs.count()
    if total == 0:
        raise ValueError("该科目暂无该类型题目")
    select_count = min(size, total)
    question_pool = list(questions_qs)
    if total <= select_count:
        return question_pool, total
    selected = sample(question_pool, select_count)
    return selected, select_count


def get_user_wrong_question_ids(user, question_ids: List[int]):
    if not question_ids or not user.is_authenticated:
        return set()
    return set(
        WrongBookEntry.objects.filter(user=user, question_id__in=question_ids)
        .values_list("question_id", flat=True)
    )


def create_attempt_with_questions(
    *,
    user,
    subject: Subject,
    question_type: str,
    size: int,
    duration_seconds: int,
    mode: str = "practice",
    assignment: Optional[ExamAssignment] = None,
):
    questions, _ = build_questions(subject, question_type, size)
    total_score = sum(resolve_score(question.question_type, question.score) for question in questions)
    with transaction.atomic():
        attempt = PracticeAttempt.objects.create(
            user=user,
            subject=subject,
            question_type=question_type,
            duration_seconds=duration_seconds,
            total_questions=len(questions),
            total_score=total_score,
            mode=mode,
            assignment=assignment,
        )
        for index, question in enumerate(questions, start=1):
            PracticeAttemptItem.objects.create(
                attempt=attempt,
                question=question,
                order=index,
            )

    serializer = PracticeQuestionSerializer(questions, many=True)
    question_payload = serializer.data
    for index, payload in enumerate(question_payload, start=1):
        payload["order"] = index

    expires_at, remaining = get_remaining_seconds(attempt)
    return attempt, question_payload, expires_at, remaining


def parse_to_aware_datetime(value: Optional[str]):
    if not value:
        return None
    dt = parse_datetime(value)
    if not dt:
        return None
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone.get_current_timezone())
    return dt


def evaluate_attempt_items(
    attempt: PracticeAttempt,
    answer_map: Optional[Dict[int, str]] = None,
):
    items = list(attempt.items.select_related("question"))
    correct_count = 0
    obtained_score = 0
    total_score_value = 0

    for item in items:
        if answer_map is not None:
            item.user_answer = answer_map.get(item.question_id, "")

        if attempt.question_type == "objective":
            normalized_answer = (item.user_answer or "").strip().upper()
            correct_answer = (item.question.answer or "").strip().upper()
            item.is_correct = bool(normalized_answer) and normalized_answer == correct_answer
            question_score = resolve_score(item.question.question_type, item.question.score)
            total_score_value += question_score
            if item.is_correct:
                correct_count += 1
                item.awarded_score = question_score
                obtained_score += question_score
            else:
                item.awarded_score = 0
        else:
            item.is_correct = None
            question_score = resolve_score(item.question.question_type, item.question.score)
            total_score_value += question_score

    PracticeAttemptItem.objects.bulk_update(items, ["user_answer", "is_correct", "awarded_score"])
    return items, correct_count, obtained_score, total_score_value


def ensure_attempt_expiration(attempt: PracticeAttempt):
    expire_time, remaining = get_remaining_seconds(attempt)
    if attempt.status == "ongoing" and remaining <= 0:
        if attempt.question_type == "objective":
            items, correct_count, obtained_score, total_score_value = evaluate_attempt_items(attempt)
            attempt.correct_count = correct_count
            attempt.total_score = total_score_value
            attempt.obtained_score = obtained_score
            fields = [
                "correct_count",
                "total_score",
                "obtained_score",
                "status",
                "submitted_at",
            ]
        else:
            items = None
            attempt.total_score = 0
            fields = ["total_score", "status", "submitted_at", "is_review_required"]
        attempt.status = "expired"
        attempt.submitted_at = timezone.now()
        if attempt.question_type == "subjective":
            attempt.is_review_required = True
        attempt.save(update_fields=fields)
        return expire_time, remaining, items
    return expire_time, remaining, None


class SubjectListView(APIView):
    """返回所有可选科目。"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        subjects = Subject.objects.all().order_by("name")
        serializer = SubjectSerializer(subjects, many=True)
        return Response({
            "code": 200,
            "info": "获取科目成功",
            "data": serializer.data,
        })


class QuestionPracticeView(APIView):
    """按照科目和题型随机返回题目。"""

    permission_classes = [IsAuthenticated]

    def get(self, request):  # type: ignore[override]
        subject_id = request.GET.get("subject_id")
        question_type = request.GET.get("question_type", "objective")
        size = int(request.GET.get("size", 10))

        if not subject_id:
            return Response({"code": 400, "info": "缺少subject_id参数", "data": []})

        if question_type not in {"objective", "subjective"}:
            return Response({"code": 400, "info": "题型参数不正确", "data": []})

        try:
            subject = Subject.objects.get(id=subject_id)
        except Subject.DoesNotExist:
            return Response({"code": 404, "info": "科目不存在", "data": []})

        questions: QuerySet[Question] = Question.objects.filter(
            subject=subject,
            question_type=question_type,
        )

        if not questions.exists():
            return Response({"code": 404, "info": "该科目暂无符合条件的题目", "data": []})

        total = questions.count()
        count = min(size, total)

        if total <= count:
            selected = list(questions)
        else:
            ids = list(questions.values_list("id", flat=True))
            selected_ids = sample(ids, count)
            selected = list(questions.filter(id__in=selected_ids))

        serializer = QuestionSerializer(selected, many=True)
        return Response({
            "code": 200,
            "info": "获取题目成功",
            "data": serializer.data,
        })


class PracticeAttemptStartView(APIView):
    """创建一次新的练习并返回题目列表。"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        subject_id = request.data.get("subject_id")
        question_type = request.data.get("question_type", "objective")
        size_raw = request.data.get("size")
        duration_raw = request.data.get("duration_seconds")

        if not subject_id:
            return Response({"code": 400, "info": "缺少subject_id参数"})

        if question_type not in {"objective", "subjective"}:
            return Response({"code": 400, "info": "题型参数不正确"})

        try:
            subject = Subject.objects.get(id=subject_id)
        except Subject.DoesNotExist:
            return Response({"code": 404, "info": "科目不存在"})

        try:
            duration_seconds = int(duration_raw) if duration_raw else 1800
        except (TypeError, ValueError):
            duration_seconds = 1800

        try:
            size = int(size_raw) if size_raw else QUESTION_DEFAULT_SIZE[question_type]
        except (TypeError, ValueError):
            size = QUESTION_DEFAULT_SIZE[question_type]

        try:
            attempt, question_payload, expires_at, remaining = create_attempt_with_questions(
                user=request.user,
                subject=subject,
                question_type=question_type,
                size=size,
                duration_seconds=duration_seconds,
                mode="practice",
                assignment=None,
            )
        except ValueError as exc:
            return Response({"code": 404, "info": str(exc)})

        return Response({
            "code": 200,
            "info": "练习创建成功",
            "data": {
                "attempt_id": attempt.id,
                "subject": SubjectSerializer(subject).data,
                "question_type": question_type,
                "duration_seconds": attempt.duration_seconds,
                "started_at": attempt.started_at,
                "expires_at": expires_at,
                "remaining_seconds": remaining,
                "mode": attempt.mode,
                "questions": question_payload,
            },
        })


class PracticeAttemptSubmitView(APIView):
    """提交练习答案并返回结果。"""

    permission_classes = [IsAuthenticated]

    def post(self, request, attempt_id: int):
        answers = request.data.get("answers", [])
        if not isinstance(answers, list):
            return Response({"code": 400, "info": "答案格式不正确"})

        with transaction.atomic():
            try:
                attempt = PracticeAttempt.objects.select_for_update().get(
                    id=attempt_id,
                    user=request.user,
                )
            except PracticeAttempt.DoesNotExist:
                return Response({"code": 404, "info": "练习不存在"})

            if attempt.status in {"completed", "expired"}:
                serializer = PracticeAttemptSerializer(attempt)
                items_qs = attempt.items.select_related("question")
                question_ids = list(items_qs.values_list("question_id", flat=True))
                wrong_ids = get_user_wrong_question_ids(request.user, question_ids)
                items = PracticeAttemptItemSerializer(
                    items_qs,
                    many=True,
                    context={
                        "show_solution": attempt.question_type == "objective",
                        "wrong_question_ids": wrong_ids,
                    },
                )
                return Response({
                    "code": 200,
                    "info": "该练习已提交",
                    "data": {"attempt": serializer.data, "items": items.data},
                })

            answer_map = {
                int(item.get("question_id")): (item.get("user_answer") or "")
                for item in answers
                if item.get("question_id") is not None
            }

            now = timezone.now()
            expire_time = get_expire_time(attempt)
            is_expired = now > expire_time

            items, correct_count, obtained_score, total_score_value = evaluate_attempt_items(attempt, answer_map)

            update_fields = ["status", "submitted_at"]
            if attempt.question_type == "objective":
                attempt.correct_count = correct_count
                attempt.total_score = total_score_value
                attempt.obtained_score = obtained_score
                update_fields.extend(["correct_count", "total_score", "obtained_score"])
            else:
                attempt.is_review_required = True
                update_fields.append("is_review_required")
                if attempt.total_score == 0 and total_score_value:
                    attempt.total_score = total_score_value
                    update_fields.append("total_score")

            attempt.status = "expired" if is_expired else "completed"
            attempt.submitted_at = now
            attempt.save(update_fields=update_fields)

        serializer = PracticeAttemptSerializer(attempt)
        question_ids = [item.question_id for item in items]
        wrong_ids = get_user_wrong_question_ids(request.user, question_ids)
        item_serializer = PracticeAttemptItemSerializer(
            items,
            many=True,
            context={
                "show_solution": attempt.question_type == "objective",
                "wrong_question_ids": wrong_ids,
            },
        )

        return Response({
            "code": 200,
            "info": "练习提交成功" if not is_expired else "练习已超时并自动提交",
            "data": {
                "attempt": serializer.data,
                "items": item_serializer.data,
            },
        })


class PracticeAttemptDetailView(APIView):
    """查看单次练习详情。"""

    permission_classes = [IsAuthenticated]

    def get(self, request, attempt_id: int):
        try:
            attempt = PracticeAttempt.objects.get(id=attempt_id, user=request.user)
        except PracticeAttempt.DoesNotExist:
            return Response({"code": 404, "info": "练习不存在"})

        expire_time, remaining, _ = ensure_attempt_expiration(attempt)
        attempt.refresh_from_db()
        serializer = PracticeAttemptSerializer(attempt)
        items_qs = attempt.items.select_related("question")
        question_ids = list(items_qs.values_list("question_id", flat=True))
        wrong_ids = get_user_wrong_question_ids(request.user, question_ids)
        item_serializer = PracticeAttemptItemSerializer(
            items_qs,
            many=True,
            context={
                "show_solution": attempt.status in {"completed", "expired"} and attempt.question_type == "objective",
                "wrong_question_ids": wrong_ids,
            },
        )
        return Response({
            "code": 200,
            "info": "获取练习详情成功",
            "data": {
                "attempt": serializer.data,
                "items": item_serializer.data,
                "expires_at": expire_time,
                "remaining_seconds": remaining,
            },
        })


class PracticeAttemptHistoryView(APIView):
    """返回学生历史练习记录。"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        subject_id = request.GET.get("subject_id")
        question_type = request.GET.get("question_type")
        status = request.GET.get("status")
        mode = request.GET.get("mode")
        limit_raw = request.GET.get("limit")
        page_raw = request.GET.get("page")
        page_size_raw = request.GET.get("page_size") or limit_raw

        attempts = PracticeAttempt.objects.filter(user=request.user)
        if subject_id:
            attempts = attempts.filter(subject_id=subject_id)
        if question_type in {"objective", "subjective"}:
            attempts = attempts.filter(question_type=question_type)
        if status:
            attempts = attempts.filter(status=status)
        else:
            attempts = attempts.exclude(status="ongoing")
        if mode in {"practice", "exam"}:
            attempts = attempts.filter(mode=mode)

        def parse_positive_int(value, default):
            if value is None:
                return default
            try:
                parsed = int(value)
            except (TypeError, ValueError):
                return default
            return parsed if parsed > 0 else default

        page = parse_positive_int(page_raw, 1)
        page_size = parse_positive_int(page_size_raw, 10)

        attempts = attempts.order_by("-started_at")
        total = attempts.count()
        if page_size:
            start = (page - 1) * page_size
            end = start + page_size
            attempts = attempts[start:end]
        serializer = PracticeAttemptSerializer(attempts, many=True)
        return Response({
            "code": 200,
            "info": "获取历史记录成功",
            "data": {
                "results": serializer.data,
                "total": total,
                "page": page,
                "page_size": page_size,
            },
        })


class PracticeAttemptOngoingView(APIView):
    """进行中的练习列表。"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        mode = request.GET.get("mode")
        attempts = PracticeAttempt.objects.filter(user=request.user, status="ongoing").order_by("-started_at")
        if mode in {"practice", "exam"}:
            attempts = attempts.filter(mode=mode)
        data = []
        for attempt in attempts:
            expire_time, remaining, _ = ensure_attempt_expiration(attempt)
            if attempt.status != "ongoing":
                continue
            data.append({
                "id": attempt.id,
                "subject_id": attempt.subject_id,
                "subject_name": attempt.subject.name,
                "question_type": attempt.question_type,
                "total_questions": attempt.total_questions,
                "started_at": attempt.started_at,
                "expires_at": expire_time,
                "remaining_seconds": remaining,
                 "mode": attempt.mode,
                 "assignment_id": attempt.assignment_id,
                 "assignment_title": attempt.assignment.title if attempt.assignment else None,
            })
        return Response({
            "code": 200,
            "info": "获取进行中练习成功",
            "data": data,
        })


class PracticeAttemptPendingReviewView(APIView):
    """主观题等待教师批阅的练习。"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        mode = request.GET.get("mode")
        attempts = PracticeAttempt.objects.filter(
            user=request.user,
            question_type="subjective",
            is_review_required=True,
            status__in=["completed", "expired"],
        ).order_by("-submitted_at")

        if mode in {"practice", "exam"}:
            attempts = attempts.filter(mode=mode)

        data = [
            {
                "id": attempt.id,
                "subject_id": attempt.subject_id,
                "subject_name": attempt.subject.name,
                "submitted_at": attempt.submitted_at,
                "status": attempt.status,
                "mode": attempt.mode,
                "assignment_id": attempt.assignment_id,
                "assignment_title": attempt.assignment.title if attempt.assignment else None,
            }
            for attempt in attempts
        ]
        return Response({
            "code": 200,
            "info": "获取待批阅练习成功",
            "data": data,
        })


class PracticeAttemptSaveAnswersView(APIView):
    """保存练习中的作答，不计算成绩。"""

    permission_classes = [IsAuthenticated]

    def post(self, request, attempt_id: int):
        answers = request.data.get("answers", [])
        if not isinstance(answers, list):
            return Response({"code": 400, "info": "答案格式不正确"})

        with transaction.atomic():
            try:
                attempt = PracticeAttempt.objects.select_for_update().get(
                    id=attempt_id,
                    user=request.user,
                )
            except PracticeAttempt.DoesNotExist:
                return Response({"code": 404, "info": "练习不存在"})

            expire_time, remaining, _ = ensure_attempt_expiration(attempt)
            if attempt.status != "ongoing":
                return Response({"code": 400, "info": "练习已结束"})

            answer_map = {
                int(item.get("question_id")): (item.get("user_answer") or "")
                for item in answers
                if item.get("question_id") is not None
            }

            items_to_update = []
            for item in attempt.items.all():
                if item.question_id in answer_map:
                    new_answer = answer_map[item.question_id]
                    if (item.user_answer or "") != new_answer:
                        item.user_answer = new_answer
                        items_to_update.append(item)

            if items_to_update:
                PracticeAttemptItem.objects.bulk_update(items_to_update, ["user_answer"])

        return Response({
            "code": 200,
            "info": "作答已保存",
            "data": {
                "remaining_seconds": remaining,
                "expires_at": expire_time,
            },
        })


class WrongBookEntryListView(APIView):
    """学生错题本：按科目返回或新增错题。"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        subject_id = request.GET.get("subject_id")
        page_raw = request.GET.get("page")
        page_size_raw = request.GET.get("page_size")

        def parse_positive_int(value, default):
            if value is None:
                return default
            try:
                parsed = int(value)
            except (TypeError, ValueError):
                return default
            return parsed if parsed > 0 else default

        page = parse_positive_int(page_raw, 1)
        page_size = parse_positive_int(page_size_raw, 10)

        base_qs = WrongBookEntry.objects.filter(user=request.user).select_related("subject", "question")
        subject_summary = list(
            base_qs.values("subject_id", "subject__name")
            .annotate(total=Count("id"))
            .order_by("subject__name")
        )

        entries = base_qs
        if subject_id:
            entries = entries.filter(subject_id=subject_id)

        entries = entries.order_by("-last_wrong_at", "-id")
        total = entries.count()
        start = (page - 1) * page_size
        end = start + page_size
        entries = entries[start:end]

        serializer = WrongBookEntrySerializer(entries, many=True)
        subjects_payload = [
            {
                "id": item["subject_id"],
                "name": item["subject__name"],
                "count": item["total"],
            }
            for item in subject_summary
            if item["subject_id"] is not None
        ]

        return Response({
            "code": 200,
            "info": "获取错题本成功",
            "data": {
                "results": serializer.data,
                "total": total,
                "page": page,
                "page_size": page_size,
                "subjects": subjects_payload,
            },
        })

    def post(self, request):
        attempt_item_id = request.data.get("attempt_item_id")
        if not attempt_item_id:
            return Response({"code": 400, "info": "缺少题目记录"})

        try:
            item = PracticeAttemptItem.objects.select_related("attempt", "attempt__user", "question", "question__subject").get(
                id=attempt_item_id,
                attempt__user=request.user,
            )
        except PracticeAttemptItem.DoesNotExist:
            return Response({"code": 404, "info": "题目记录不存在"})

        if item.attempt.status == "ongoing":
            return Response({"code": 400, "info": "练习尚未结束，无法加入错题本"})

        if item.question.question_type == "subjective" and item.attempt.is_review_required:
            return Response({"code": 400, "info": "主观题尚在批阅中，待老师批阅后再加入错题本"})

        max_score = resolve_score(item.question.question_type, item.question.score)
        is_wrong = False
        if item.question.question_type == "objective":
            is_wrong = item.is_correct is False
        else:
            is_wrong = (item.awarded_score or 0) < max_score

        if not is_wrong:
            return Response({"code": 400, "info": "该题未判定为错题，无需加入错题本"})

        entry, created = WrongBookEntry.objects.get_or_create(
            user=request.user,
            question=item.question,
            defaults={
                "subject": item.question.subject,
                "last_attempt": item.attempt,
                "last_attempt_item": item,
                "last_user_answer": item.user_answer or "",
            },
        )

        if not created:
            entry.subject = item.question.subject
            entry.last_attempt = item.attempt
            entry.last_attempt_item = item
            entry.last_user_answer = item.user_answer or ""
            entry.wrong_times += 1
            entry.save()

        serializer = WrongBookEntrySerializer(entry)
        return Response({"code": 200, "info": "已加入错题本", "data": serializer.data})


class WrongBookEntryDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, entry_id: int):
        try:
            entry = WrongBookEntry.objects.get(id=entry_id, user=request.user)
        except WrongBookEntry.DoesNotExist:
            return Response({"code": 404, "info": "错题不存在"})
        entry.delete()
        return Response({"code": 200, "info": "错题已移出错题本"})


class ExamAssignmentListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if getattr(request.user, "role", "") != "teacher":
            return Response({"code": 403, "info": "仅教师可操作"})
        assignments = ExamAssignment.objects.filter(created_by=request.user).select_related("subject").order_by("-start_time")
        serializer = ExamAssignmentSerializer(assignments, many=True)
        data = serializer.data
        for idx, assignment in enumerate(assignments):
            data[idx]["total_attempts"] = assignment.attempts.count()
            data[idx]["pending_reviews"] = assignment.attempts.filter(
                question_type="subjective",
                is_review_required=True,
            ).count()
        return Response({"code": 200, "info": "获取考试任务成功", "data": data})

    def post(self, request):
        if getattr(request.user, "role", "") != "teacher":
            return Response({"code": 403, "info": "仅教师可操作"})

        title = (request.data.get("title") or "").strip()
        subject_id = request.data.get("subject_id")
        question_type = request.data.get("question_type", "objective")
        duration_seconds = int(request.data.get("duration_seconds") or 1800)
        question_count = request.data.get("question_count")
        start_time = parse_to_aware_datetime(request.data.get("start_time"))
        end_time = parse_to_aware_datetime(request.data.get("end_time"))
        description = request.data.get("description", "")

        if not title:
            return Response({"code": 400, "info": "考试标题不能为空"})

        try:
            subject = Subject.objects.get(id=subject_id)
        except Subject.DoesNotExist:
            return Response({"code": 404, "info": "科目不存在"})

        if question_type not in {"objective", "subjective"}:
            return Response({"code": 400, "info": "题型参数不正确"})

        if not start_time or not end_time:
            return Response({"code": 400, "info": "请提供考试开始/结束时间"})
        if end_time <= start_time:
            return Response({"code": 400, "info": "结束时间需晚于开始时间"})

        try:
            question_count = int(question_count) if question_count else QUESTION_DEFAULT_SIZE[question_type]
        except (TypeError, ValueError):
            question_count = QUESTION_DEFAULT_SIZE[question_type]

        status_value = request.data.get("status", "published")
        if status_value not in {"draft", "published", "closed"}:
            status_value = "published"

        assignment = ExamAssignment.objects.create(
            title=title,
            subject=subject,
            question_type=question_type,
            question_count=question_count,
            duration_seconds=duration_seconds,
            start_time=start_time,
            end_time=end_time,
            status=status_value,
            description=description,
            created_by=request.user,
        )

        serializer = ExamAssignmentSerializer(assignment)
        payload = serializer.data
        payload["total_attempts"] = 0
        payload["pending_reviews"] = 0
        return Response({"code": 200, "info": "考试创建成功", "data": payload})


class ExamAssignmentAvailableView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        assignments = ExamAssignment.objects.filter(status="published").select_related("subject", "created_by").order_by("start_time")
        data = []
        for assignment in assignments:
            attempt = assignment.attempts.filter(user=request.user).order_by("-started_at").first()
            serializer = ExamAssignmentSerializer(assignment)
            payload = serializer.data
            payload["attempt_id"] = attempt.id if attempt else None
            payload["attempt_status"] = attempt.status if attempt else None
            payload["attempt_mode"] = attempt.mode if attempt else None
            data.append(payload)
        return Response({"code": 200, "info": "获取考试列表成功", "data": data})


class ExamAssignmentStartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, assignment_id: int):
        assignment = get_object_or_404(ExamAssignment.objects.select_related("subject"), id=assignment_id)

        if assignment.status != "published":
            return Response({"code": 400, "info": "考试未发布"})

        now = timezone.now()
        if now < assignment.start_time:
            return Response({"code": 400, "info": "考试尚未开始"})
        if now > assignment.end_time:
            return Response({"code": 400, "info": "考试已结束"})

        existing_attempt = assignment.attempts.filter(user=request.user).order_by("-started_at").first()
        if existing_attempt:
            expire_time, remaining, _ = ensure_attempt_expiration(existing_attempt)
            if existing_attempt.status == "ongoing":
                return Response({
                    "code": 200,
                    "info": "已有进行中的考试，已为你恢复进度",
                    "data": {
                        "attempt_id": existing_attempt.id,
                        "mode": existing_attempt.mode,
                        "remaining_seconds": remaining,
                        "expires_at": expire_time,
                        "assignment": ExamAssignmentSerializer(assignment).data,
                        "resumed": True,
                    },
                })
            return Response({"code": 400, "info": "你已完成该考试"})

        try:
            attempt, question_payload, expires_at, remaining = create_attempt_with_questions(
                user=request.user,
                subject=assignment.subject,
                question_type=assignment.question_type,
                size=assignment.question_count,
                duration_seconds=assignment.duration_seconds,
                mode="exam",
                assignment=assignment,
            )
        except ValueError as exc:
            return Response({"code": 404, "info": str(exc)})

        assignment_data = ExamAssignmentSerializer(assignment).data
        return Response({
            "code": 200,
            "info": "考试试卷生成成功",
            "data": {
                "attempt_id": attempt.id,
                "assignment": assignment_data,
                "subject": SubjectSerializer(assignment.subject).data,
                "question_type": attempt.question_type,
                "duration_seconds": attempt.duration_seconds,
                "started_at": attempt.started_at,
                "expires_at": expires_at,
                "remaining_seconds": remaining,
                "mode": attempt.mode,
                "questions": question_payload,
            },
        })


class ExamAssignmentSubmissionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, assignment_id: int):
        assignment = get_object_or_404(ExamAssignment.objects.select_related("subject", "created_by"), id=assignment_id)
        if assignment.created_by_id != request.user.id:
            return Response({"code": 403, "info": "仅发布者可查看"})
        attempts = assignment.attempts.select_related("user", "subject").order_by("-started_at")
        serializer = PracticeAttemptSerializer(attempts, many=True)
        return Response({
            "code": 200,
            "info": "获取考试作答成功",
            "data": {
                "assignment": ExamAssignmentSerializer(assignment).data,
                "attempts": serializer.data,
            },
        })


class PracticeAttemptTeacherPendingReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if getattr(request.user, "role", "") != "teacher":
            return Response({"code": 403, "info": "仅教师可操作"})
        assignment_id = request.GET.get("assignment_id")
        student_id = request.GET.get("student_id")

        attempts = PracticeAttempt.objects.filter(
            question_type="subjective",
            is_review_required=True,
            status__in=["completed", "expired"],
        ).select_related("user", "subject", "assignment").order_by("-submitted_at")

        attempts = attempts.filter(
            Q(assignment__isnull=True) | Q(assignment__created_by=request.user),
        )

        if assignment_id:
            if assignment_id == "practice":
                attempts = attempts.filter(assignment__isnull=True)
            else:
                attempts = attempts.filter(assignment_id=assignment_id)

        if student_id:
            attempts = attempts.filter(user_id=student_id)

        data = [
            {
                "id": attempt.id,
                "student_id": attempt.user_id,
                "student_name": attempt.user.username,
                "subject_name": attempt.subject.name,
                "assignment_id": attempt.assignment_id,
                "assignment_title": attempt.assignment.title if attempt.assignment else None,
                "submitted_at": attempt.submitted_at,
                "status": attempt.status,
                "mode": attempt.mode,
                "question_type": attempt.question_type,
                "total_questions": attempt.total_questions,
            }
            for attempt in attempts
        ]
        return Response({"code": 200, "info": "获取待批阅试卷成功", "data": data})


class PracticeAttemptTeacherStudentPendingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if getattr(request.user, "role", "") != "teacher":
            return Response({"code": 403, "info": "仅教师可操作"})

        assignment_id = request.GET.get("assignment_id")

        attempts = PracticeAttempt.objects.filter(
            question_type="subjective",
            is_review_required=True,
            status__in=["completed", "expired"],
        ).select_related("user", "subject", "assignment").order_by("-submitted_at")

        attempts = attempts.filter(
            Q(assignment__isnull=True) | Q(assignment__created_by=request.user),
        )

        if assignment_id:
            if assignment_id == "practice":
                attempts = attempts.filter(assignment__isnull=True)
            else:
                attempts = attempts.filter(assignment_id=assignment_id)

        student_map: "OrderedDict[int, Dict[str, object]]" = OrderedDict()
        for attempt in attempts:
            entry = student_map.get(attempt.user_id)
            if not entry:
                entry = {
                    "student_id": attempt.user_id,
                    "student_name": attempt.user.username,
                    "pending_count": 0,
                    "latest_submitted_at": attempt.submitted_at,
                    "attempts": [],
                }
                student_map[attempt.user_id] = entry
            entry["pending_count"] += 1
            if not entry["latest_submitted_at"] or (attempt.submitted_at and attempt.submitted_at > entry["latest_submitted_at"]):
                entry["latest_submitted_at"] = attempt.submitted_at
            entry["attempts"].append({
                "id": attempt.id,
                "assignment_id": attempt.assignment_id,
                "assignment_title": attempt.assignment.title if attempt.assignment else None,
                "subject_name": attempt.subject.name,
                "submitted_at": attempt.submitted_at,
                "status": attempt.status,
                "mode": attempt.mode,
                "question_type": attempt.question_type,
                "total_questions": attempt.total_questions,
            })

        data = list(student_map.values())
        return Response({"code": 200, "info": "获取待批阅学生列表成功", "data": data})


class PracticeAttemptTeacherDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, attempt_id: int):
        if getattr(request.user, "role", "") != "teacher":
            return Response({"code": 403, "info": "仅教师可操作"})
        attempt = get_object_or_404(
            PracticeAttempt.objects.select_related("user", "subject", "assignment"),
            id=attempt_id,
        )
        if attempt.assignment and attempt.assignment.created_by_id != request.user.id:
            return Response({"code": 403, "info": "无权查看该试卷"})

        serializer = PracticeAttemptSerializer(attempt)
        item_serializer = PracticeAttemptItemSerializer(
            attempt.items.select_related("question"),
            many=True,
            context={"show_solution": True},
        )
        return Response({
            "code": 200,
            "info": "获取试卷详情成功",
            "data": {
                "attempt": serializer.data,
                "items": item_serializer.data,
            },
        })


class PracticeAttemptReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, attempt_id: int):
        if getattr(request.user, "role", "") != "teacher":
            return Response({"code": 403, "info": "仅教师可操作"})

        with transaction.atomic():
            try:
                attempt = PracticeAttempt.objects.select_for_update().select_related("assignment").get(id=attempt_id)
            except PracticeAttempt.DoesNotExist:
                return Response({"code": 404, "info": "试卷不存在"})

            if attempt.assignment and attempt.assignment.created_by_id != request.user.id:
                return Response({"code": 403, "info": "无权批阅该试卷"})
            if attempt.question_type != "subjective":
                return Response({"code": 400, "info": "仅主观题需要批阅"})
            if not attempt.is_review_required:
                return Response({"code": 400, "info": "该试卷无需批阅"})

            item_payload = request.data.get("items", [])
            if not isinstance(item_payload, list) or not item_payload:
                return Response({"code": 400, "info": "请提交题目得分"})

            items = list(attempt.items.select_related("question"))
            if not items:
                return Response({"code": 400, "info": "试卷题目数据缺失"})

            item_map = {item.id: item for item in items}
            updated_items = []
            provided_ids = set()

            for entry in item_payload:
                try:
                    item_id = int(entry.get("id"))
                except (TypeError, ValueError, AttributeError):
                    continue
                if item_id not in item_map:
                    continue
                provided_ids.add(item_id)
                try:
                    raw_score = int(entry.get("awarded_score", 0))
                except (TypeError, ValueError):
                    raw_score = 0
                item = item_map[item_id]
                max_score = resolve_score(item.question.question_type, item.question.score)
                clamped_score = max(0, min(raw_score, max_score))
                if item.awarded_score != clamped_score:
                    item.awarded_score = clamped_score
                    updated_items.append(item)

            if not provided_ids:
                return Response({"code": 400, "info": "请至少为一道题设置得分"})

            if updated_items:
                PracticeAttemptItem.objects.bulk_update(updated_items, ["awarded_score"])

            total_obtained = sum(item.awarded_score for item in item_map.values())
            total_possible = sum(
                resolve_score(item.question.question_type, item.question.score)
                for item in item_map.values()
            )

            review_comment = request.data.get("review_comment", "")

            if attempt.total_score == 0 and total_possible:
                attempt.total_score = total_possible

            possible = attempt.total_score or total_possible or 0
            attempt.obtained_score = max(0, min(total_obtained, possible))
            attempt.review_comment = review_comment
            attempt.is_review_required = False
            attempt.reviewed_by = request.user
            attempt.reviewed_at = timezone.now()
            attempt.save(update_fields=[
                "obtained_score",
                "total_score",
                "review_comment",
                "is_review_required",
                "reviewed_by",
                "reviewed_at",
            ])

        serializer = PracticeAttemptSerializer(attempt)
        item_serializer = PracticeAttemptItemSerializer(
            attempt.items.select_related("question"),
            many=True,
            context={"show_solution": True},
        )
        return Response({
            "code": 200,
            "info": "批阅完成",
            "data": {
                "attempt": serializer.data,
                "items": item_serializer.data,
            },
        })
