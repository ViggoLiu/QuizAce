import json
from collections import OrderedDict
from datetime import timedelta
from random import sample
from typing import Dict, List, Optional, Tuple

from django.db import transaction
from django.db.models import Q, QuerySet, Count, Max
from django.db.models.functions import TruncDate
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .constants import OBJECTIVE_SCORE_PER_QUESTION, resolve_score
from .models import (
    ExamAssignment,
    PracticeAttempt,
    PracticeAttemptItem,
    QUESTION_DRAFT_STATUS_CHOICES,
    QUESTION_SOURCE_CHOICES,
    Question,
    QuestionDraft,
    Subject,
    WrongBookEntry,
)
from .serializers import (
    ExamAssignmentSerializer,
    PracticeAttemptItemSerializer,
    PracticeAttemptSerializer,
    PracticeQuestionSerializer,
    QuestionCreateSerializer,
    QuestionDraftSerializer,
    QuestionSerializer,
    SubjectSerializer,
    WrongBookEntrySerializer,
)


QUESTION_DEFAULT_SIZE = {
    "objective": 10,
    "subjective": 5,
}


def resolve_subject_identifier(value):
    if not value:
        raise ValueError("缺少科目信息")
    try:
        subject_id = int(value)
    except (TypeError, ValueError):
        name = str(value).strip()
        if not name:
            raise ValueError("科目名称不能为空")
        subject, _ = Subject.objects.get_or_create(name=name)
        return subject
    else:
        try:
            return Subject.objects.get(id=subject_id)
        except Subject.DoesNotExist as exc:
            raise ValueError("科目不存在") from exc

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
        status="ready",
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


def build_solution_visibility_map(attempt: PracticeAttempt):
    base = {"objective": False, "subjective": False}
    if attempt.status not in {"completed", "expired"}:
        return base
    if attempt.question_type == "objective":
        base["objective"] = True
        return base
    if attempt.question_type == "subjective":
        base["subjective"] = not attempt.is_review_required
        return base
    # mixed 或其他情况
    base["objective"] = True
    base["subjective"] = not attempt.is_review_required
    return base


def create_attempt_with_questions(
    *,
    user,
    subject: Subject,
    question_type: str,
    size: int,
    duration_seconds: int,
    mode: str = "practice",
    assignment: Optional[ExamAssignment] = None,
    preset_questions: Optional[List[Question]] = None,
    score_overrides: Optional[Dict[int, int]] = None,
):
    score_overrides = score_overrides or {}
    if preset_questions is None:
        if question_type == "mixed":
            raise ValueError("综合试卷必须提供固定题目")
        questions, _ = build_questions(subject, question_type, size)
    else:
        questions = list(preset_questions)

    question_scores = []
    total_score = 0
    for question in questions:
        score_value = score_overrides.get(question.id)
        if score_value is None:
            score_value = resolve_score(question.question_type, question.score)
        question_scores.append((question, score_value))
        total_score += score_value

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
        for index, (question, score_value) in enumerate(question_scores, start=1):
            PracticeAttemptItem.objects.create(
                attempt=attempt,
                question=question,
                order=index,
                expected_score=score_value,
            )

    serializer = PracticeQuestionSerializer([q for q, _ in question_scores], many=True)
    question_payload = serializer.data
    for index, payload in enumerate(question_payload, start=1):
        payload["order"] = index
        override_score = score_overrides.get(payload["id"])
        if override_score is not None:
            payload["score"] = override_score

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
    has_subjective = False

    for item in items:
        if answer_map is not None:
            item.user_answer = answer_map.get(item.question_id, "")

        question_score = item.expected_score or resolve_score(item.question.question_type, item.question.score)
        total_score_value += question_score
        if item.question.question_type == "objective":
            normalized_answer = (item.user_answer or "").strip().upper()
            correct_answer = (item.question.answer or "").strip().upper()
            item.is_correct = bool(normalized_answer) and normalized_answer == correct_answer
            if item.is_correct:
                correct_count += 1
                item.awarded_score = question_score
                obtained_score += question_score
            else:
                item.awarded_score = 0
        else:
            has_subjective = True
            item.is_correct = None

    PracticeAttemptItem.objects.bulk_update(items, ["user_answer", "is_correct", "awarded_score"])
    return items, correct_count, obtained_score, total_score_value, has_subjective


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
            status="ready",
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
                            "solution_visibility": build_solution_visibility_map(attempt),
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

            items, correct_count, obtained_score, total_score_value, has_subjective = evaluate_attempt_items(attempt, answer_map)

            update_fields = ["status", "submitted_at", "total_score", "correct_count", "obtained_score"]
            attempt.correct_count = correct_count
            attempt.total_score = total_score_value
            attempt.obtained_score = obtained_score

            if has_subjective:
                attempt.is_review_required = True
                update_fields.append("is_review_required")

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
                "solution_visibility": build_solution_visibility_map(attempt),
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
                "solution_visibility": build_solution_visibility_map(attempt),
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
        if question_type in {"objective", "subjective", "mixed"}:
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
            question_type__in=["subjective", "mixed"],
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


class TeacherQuestionSubjectSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if getattr(request.user, "role", "") != "teacher":
            return Response({"code": 403, "info": "仅教师可操作"})

        qs = (
            Question.objects.filter(created_by=request.user)
            .values("subject_id", "subject__name")
            .annotate(
                total=Count("id"),
                objective_count=Count("id", filter=Q(question_type="objective")),
                subjective_count=Count("id", filter=Q(question_type="subjective")),
                last_updated=Max("updated_at"),
            )
            .order_by("-last_updated", "subject__name")
        )

        data = [
            {
                "subject_id": item["subject_id"],
                "subject_name": item["subject__name"],
                "total_questions": item["total"],
                "objective_questions": item["objective_count"],
                "subjective_questions": item["subjective_count"],
                "last_updated": item["last_updated"],
            }
            for item in qs
        ]

        return Response({"code": 200, "info": "获取科目题量成功", "data": data})


class TeacherQuestionDraftListView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request):
        if getattr(request.user, "role", "") != "teacher":
            return Response({"code": 403, "info": "仅教师可操作"})
        status_value = request.GET.get("status")
        source_mode = request.GET.get("source_mode")
        drafts = QuestionDraft.objects.filter(teacher=request.user)
        if status_value:
            drafts = drafts.filter(status=status_value)
        if source_mode in {item[0] for item in QUESTION_SOURCE_CHOICES}:
            drafts = drafts.filter(source_mode=source_mode)
        serializer = QuestionDraftSerializer(drafts, many=True)
        return Response({"code": 200, "info": "获取草稿成功", "data": serializer.data})

    def post(self, request):
        if getattr(request.user, "role", "") != "teacher":
            return Response({"code": 403, "info": "仅教师可操作"})

        source_mode = request.data.get("source_mode", "manual")
        if source_mode not in {item[0] for item in QUESTION_SOURCE_CHOICES}:
            return Response({"code": 400, "info": "来源模式不正确"})

        question_type = request.data.get("question_type", "objective")
        if question_type not in {"objective", "subjective"}:
            return Response({"code": 400, "info": "题型参数不正确"})

        subject_identifier = request.data.get("subject_id") or request.data.get("subject_name")
        try:
            subject = resolve_subject_identifier(subject_identifier)
        except ValueError as exc:
            return Response({"code": 400, "info": str(exc)})

        file_obj = request.FILES.get("file")
        media_url = request.data.get("media_url", "").strip()
        if not file_obj and not media_url:
            return Response({"code": 400, "info": "请上传题干文件或提供文件地址"})

        initial_status = "processing" if source_mode == "ocr" else "uploaded"
        draft = QuestionDraft.objects.create(
            teacher=request.user,
            subject=subject,
            question_type=question_type,
            source_mode=source_mode,
            status=initial_status,
            media=file_obj,
            media_url=media_url,
        )
        serializer = QuestionDraftSerializer(draft)
        return Response({"code": 200, "info": "题目已上传", "data": serializer.data})


class TeacherQuestionDraftDetailView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get_object(self, request, draft_id: int) -> QuestionDraft:
        return get_object_or_404(QuestionDraft, id=draft_id, teacher=request.user)

    def get(self, request, draft_id: int):
        if getattr(request.user, "role", "") != "teacher":
            return Response({"code": 403, "info": "仅教师可操作"})
        draft = self.get_object(request, draft_id)
        serializer = QuestionDraftSerializer(draft)
        return Response({"code": 200, "info": "获取草稿成功", "data": serializer.data})

    def patch(self, request, draft_id: int):
        if getattr(request.user, "role", "") != "teacher":
            return Response({"code": 403, "info": "仅教师可操作"})
        draft = self.get_object(request, draft_id)
        updatable_fields = {
            "status",
            "parsed_title",
            "parsed_content",
            "parsed_options",
            "parsed_answer",
            "parsed_analysis",
            "error_message",
        }
        payload = {}
        for field in updatable_fields:
            if field in request.data:
                payload[field] = request.data.get(field)
        if "status" in payload and payload["status"] not in {item[0] for item in QUESTION_DRAFT_STATUS_CHOICES}:
            return Response({"code": 400, "info": "状态值不正确"})
        if "parsed_options" in payload and isinstance(payload["parsed_options"], str):
            try:
                payload["parsed_options"] = json.loads(payload["parsed_options"] or "[]")
            except json.JSONDecodeError:
                return Response({"code": 400, "info": "解析选项格式不正确"})
        subject_identifier = request.data.get("subject_id") or request.data.get("subject_name")
        if subject_identifier:
            try:
                payload["subject"] = resolve_subject_identifier(subject_identifier)
            except ValueError as exc:
                return Response({"code": 400, "info": str(exc)})
        new_file = request.FILES.get("file")
        if new_file:
            draft.media = new_file
        media_url = request.data.get("media_url")
        if media_url is not None:
            payload["media_url"] = media_url
        for key, value in payload.items():
            setattr(draft, key, value)
        draft.save()
        serializer = QuestionDraftSerializer(draft)
        return Response({"code": 200, "info": "草稿已更新", "data": serializer.data})

    def delete(self, request, draft_id: int):
        if getattr(request.user, "role", "") != "teacher":
            return Response({"code": 403, "info": "仅教师可操作"})
        draft = self.get_object(request, draft_id)
        if draft.question_id:
            return Response({"code": 400, "info": "草稿已发布，无法删除"})
        draft.delete()
        return Response({"code": 200, "info": "草稿已删除"})


class TeacherQuestionDraftPublishView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, draft_id: int):
        if getattr(request.user, "role", "") != "teacher":
            return Response({"code": 403, "info": "仅教师可操作"})
        draft = get_object_or_404(QuestionDraft, id=draft_id, teacher=request.user)
        if draft.question_id:
            return Response({"code": 400, "info": "草稿已发布"})

        content = request.data.get("content") or draft.parsed_content
        if not content:
            return Response({"code": 400, "info": "请提供题干内容"})

        options_payload = request.data.get("options", None)
        if options_payload in (None, ""):
            options = draft.parsed_options
        elif isinstance(options_payload, str):
            try:
                options = json.loads(options_payload)
            except json.JSONDecodeError:
                return Response({"code": 400, "info": "选项格式解析失败"})
        else:
            options = options_payload
        answer = request.data.get("answer") or draft.parsed_answer
        analysis = request.data.get("analysis") or draft.parsed_analysis
        score_raw = request.data.get("score")
        score = None
        if score_raw not in (None, ""):
            try:
                score = int(score_raw)
            except (TypeError, ValueError):
                return Response({"code": 400, "info": "分值格式不正确"})
        subject_identifier = request.data.get("subject_id")
        if not subject_identifier:
            if draft.subject_id:
                subject_identifier = draft.subject_id
            elif draft.subject:
                subject_identifier = draft.subject.name
        if not subject_identifier:
            return Response({"code": 400, "info": "请先选择科目"})
        try:
            subject = resolve_subject_identifier(subject_identifier)
        except ValueError as exc:
            return Response({"code": 400, "info": str(exc)})

        payload = {
            "subject": subject.id,
            "question_type": draft.question_type,
            "content": content,
            "options": options,
            "answer": answer or "",
            "analysis": analysis or "",
            "score": score or resolve_score(draft.question_type, None),
            "source_mode": draft.source_mode,
            "status": "ready",
            "media_url": draft.resolved_media_url,
            "metadata": {
                "draft_id": draft.id,
                "parsed_title": draft.parsed_title,
            },
        }

        serializer = QuestionCreateSerializer(data=payload)
        if not serializer.is_valid():
            return Response({"code": 400, "info": serializer.errors})

        question = serializer.save(created_by=request.user)
        draft.status = "published"
        draft.question = question
        draft.subject = subject
        draft.save(update_fields=["status", "question", "subject", "updated_at"])

        question_serializer = QuestionSerializer(question)
        return Response({"code": 200, "info": "题目已发布", "data": question_serializer.data})


class QuestionImageUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self, request):
        if getattr(request.user, "role", "") != "teacher":
            return Response({"code": 403, "info": "仅教师可操作"})
        
        if 'image' not in request.FILES:
            return Response({"code": 400, "info": "没有上传文件"})
        
        import os
        import uuid
        from django.conf import settings
        
        image_file = request.FILES['image']
        
        # 获取科目信息（可选）
        subject = request.POST.get('subject', '')
        
        # 构建图片存储目录路径
        base_dir = os.path.join(settings.MEDIA_ROOT, 'question_images')
        
        # 如果提供了科目信息，创建科目子目录
        if subject:
            image_dir = os.path.join(base_dir, subject)
        else:
            image_dir = base_dir
        
        # 确保目录存在
        if not os.path.exists(image_dir):
            os.makedirs(image_dir)
        
        # 生成唯一文件名，保留原始扩展名
        filename_without_ext, ext = os.path.splitext(image_file.name)
        unique_filename = f"{uuid.uuid4()}{ext}"
        filepath = os.path.join(image_dir, unique_filename)
        
        # 保存文件
        with open(filepath, 'wb+') as destination:
            for chunk in image_file.chunks():
                destination.write(chunk)
        
        # 构建图片URL
        if subject:
            image_url = f"{settings.MEDIA_URL}question_images/{subject}/{unique_filename}"
        else:
            image_url = f"{settings.MEDIA_URL}question_images/{unique_filename}"
        
        return Response({"code": 200, "info": "图片上传成功", "data": {"image_url": image_url}})


class TeacherQuestionCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser, JSONParser)  # 支持处理多种格式的请求

    def post(self, request):
        if getattr(request.user, "role", "") != "teacher":
            return Response({"code": 403, "info": "仅教师可操作"})
        
        # 解析课程信息
        # 尝试从多个来源获取课程信息
        subject_info = request.data.get("subject") or request.POST.get("subject")
        
        if not subject_info:
            # 尝试从course字段获取课程信息，以兼容旧版本的前端代码
            subject_info = request.data.get("course") or request.POST.get("course")
            
            if not subject_info:
                return Response({"code": 400, "info": "缺少课程信息"})
        
        try:
            subject = resolve_subject_identifier(subject_info)
        except ValueError as e:
            return Response({"code": 400, "info": str(e)})
        
        # 准备题目数据
        question_data = request.data.copy()
        question_data["subject"] = subject.id
        # 仅移除兼容字段，避免丢失必要的subject信息
        question_data.pop("course", None)

        # 若题干为空，则根据科目信息生成占位文本，避免序列化报错
        content_value = (question_data.get("content") or "").strip()
        if not content_value:
            question_data["content"] = f"{subject.name} 图片题目"
        
        # 处理客观题选项
        if question_data.get("question_type") == "objective":
            correct_answer = request.data.get("answer")
            if not correct_answer:
                return Response({"code": 400, "info": "客观题需要设置正确答案"})
            default_options = {label: "" for label in ("A", "B", "C", "D")}
            existing_options = question_data.get("options")
            if isinstance(existing_options, dict):
                default_options.update({str(key): str(value) for key, value in existing_options.items()})
            question_data["options"] = default_options
            question_data["answer"] = correct_answer
        
        # 使用序列化器创建题目
        serializer = QuestionCreateSerializer(data=question_data)
        if serializer.is_valid():
            question = serializer.save(created_by=request.user)
            return Response({"code": 201, "info": "题目创建成功", "data": QuestionSerializer(question).data})
        else:
            return Response({"code": 400, "info": "题目创建失败", "errors": serializer.errors})

class TeacherQuestionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if getattr(request.user, "role", "") != "teacher":
            return Response({"code": 403, "info": "仅教师可操作"})
        questions = Question.objects.filter(created_by=request.user)
        status_value = request.GET.get("status")
        question_type = request.GET.get("question_type")
        subject_id = request.GET.get("subject_id")
        if status_value:
            questions = questions.filter(status=status_value)
        if question_type in {"objective", "subjective"}:
            questions = questions.filter(question_type=question_type)
        if subject_id:
            questions = questions.filter(subject_id=subject_id)
        questions = questions.order_by("-updated_at")
        serializer = QuestionSerializer(questions, many=True)
        return Response({"code": 200, "info": "获取题目成功", "data": serializer.data})


class TeacherQuestionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _ensure_teacher(self, request):
        return getattr(request.user, "role", "") == "teacher"

    def _get_question(self, request, question_id: int):
        return get_object_or_404(Question, id=question_id, created_by=request.user)

    def put(self, request, question_id: int):
        if not self._ensure_teacher(request):
            return Response({"code": 403, "info": "仅教师可操作"})
        question = self._get_question(request, question_id)

        answer_value = request.data.get("answer")
        analysis_value = request.data.get("analysis")

        if answer_value is None and analysis_value is None:
            return Response({"code": 400, "info": "请提供需要更新的内容"})

        update_fields = []
        if answer_value is not None:
            normalized_answer = str(answer_value).strip()
            if question.question_type == "objective":
                normalized_answer = normalized_answer.upper()
                if not normalized_answer:
                    return Response({"code": 400, "info": "客观题参考答案不能为空"})
            elif not normalized_answer:
                return Response({"code": 400, "info": "主观题参考答案不能为空"})
            question.answer = normalized_answer
            update_fields.append("answer")

        if analysis_value is not None:
            question.analysis = str(analysis_value)
            update_fields.append("analysis")

        if not update_fields:
            return Response({"code": 400, "info": "未检测到可更新字段"})

        update_fields.append("updated_at")
        question.save(update_fields=update_fields)
        return Response({
            "code": 200,
            "info": "题目信息已更新",
            "data": QuestionSerializer(question).data,
        })

    def delete(self, request, question_id: int):
        if not self._ensure_teacher(request):
            return Response({"code": 403, "info": "仅教师可操作"})
        question = self._get_question(request, question_id)
        question.delete()
        return Response({"code": 200, "info": "题目已删除"})

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
                is_review_required=True,
            ).count()
        return Response({"code": 200, "info": "获取考试任务成功", "data": data})

    def post(self, request):
        if getattr(request.user, "role", "") != "teacher":
            return Response({"code": 403, "info": "仅教师可操作"})

        title = (request.data.get("title") or "").strip()
        subject_id = request.data.get("subject_id")
        duration_seconds = int(request.data.get("duration_seconds") or 1800)
        question_type = request.data.get("question_type", "objective")
        question_count = request.data.get("question_count")
        start_time = parse_to_aware_datetime(request.data.get("start_time"))
        end_time = parse_to_aware_datetime(request.data.get("end_time"))
        description = request.data.get("description", "")
        raw_question_ids = request.data.get("question_ids")
        question_id_list: List[int] = []
        if raw_question_ids not in (None, "", []):
            parsed_ids = raw_question_ids
            if isinstance(raw_question_ids, str):
                try:
                    parsed_ids = json.loads(raw_question_ids)
                except json.JSONDecodeError:
                    parsed_ids = [item.strip() for item in raw_question_ids.split(",") if item.strip()]
            if not isinstance(parsed_ids, (list, tuple)):
                return Response({"code": 400, "info": "题目列表格式不正确"})
            try:
                question_id_list = [int(item) for item in parsed_ids if str(item).strip()]
            except (TypeError, ValueError):
                return Response({"code": 400, "info": "题目列表格式不正确"})
            deduped = []
            seen = set()
            for qid in question_id_list:
                if qid not in seen:
                    deduped.append(qid)
                    seen.add(qid)
            question_id_list = deduped
        use_custom_questions = bool(question_id_list)

        if not title:
            return Response({"code": 400, "info": "考试标题不能为空"})

        try:
            subject = Subject.objects.get(id=subject_id)
        except Subject.DoesNotExist:
            return Response({"code": 404, "info": "科目不存在"})

        if use_custom_questions:
            question_type = "mixed"
        elif question_type not in {"objective", "subjective"}:
            return Response({"code": 400, "info": "题型参数不正确"})

        if not start_time or not end_time:
            return Response({"code": 400, "info": "请提供考试开始/结束时间"})
        if end_time <= start_time:
            return Response({"code": 400, "info": "结束时间需晚于开始时间"})

        if use_custom_questions:
            if len(question_id_list) != 10:
                return Response({"code": 400, "info": "请勾选 10 道题（5 道客观题 + 5 道主观题）"})
            questions = list(
                Question.objects.filter(id__in=question_id_list, created_by=request.user, status="ready")
            )
            if len(questions) != len(question_id_list):
                return Response({"code": 400, "info": "题目列表中包含无效或无权限的题目"})
            question_map = {question.id: question for question in questions}
            for qid in question_id_list:
                if question_map[qid].subject_id != subject.id:
                    return Response({"code": 400, "info": "题目科目与所选科目不一致"})
            objective_ids = [qid for qid in question_id_list if question_map[qid].question_type == "objective"]
            subjective_ids = [qid for qid in question_id_list if question_map[qid].question_type == "subjective"]
            if len(objective_ids) != 5 or len(subjective_ids) != 5:
                return Response({"code": 400, "info": "请选择 5 道客观题与 5 道主观题"})
            question_count = len(question_id_list)
        else:
            try:
                question_count = int(question_count) if question_count else QUESTION_DEFAULT_SIZE[question_type]
            except (TypeError, ValueError):
                question_count = QUESTION_DEFAULT_SIZE[question_type]

        status_value = request.data.get("status", "published")
        if status_value not in {"draft", "published", "closed"}:
            status_value = "published"

        raw_per_score = request.data.get("per_question_score")
        if raw_per_score in (None, ""):
            per_question_score = 10 if use_custom_questions else resolve_score(question_type, None)
        else:
            try:
                per_question_score = max(1, int(raw_per_score))
            except (TypeError, ValueError):
                return Response({"code": 400, "info": "分值格式不正确"})

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
            question_ids=question_id_list,
            per_question_score=per_question_score,
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

        preset_questions = None
        score_overrides = None
        if assignment.question_ids:
            question_qs = Question.objects.filter(id__in=assignment.question_ids)
            question_map = {question.id: question for question in question_qs}
            missing_ids = [qid for qid in assignment.question_ids if qid not in question_map]
            if missing_ids:
                return Response({"code": 400, "info": "试卷内存在已被删除的题目，暂无法生成"})
            ordered_questions = [question_map[qid] for qid in assignment.question_ids]
            invalid_subject = next((q for q in ordered_questions if q.subject_id != assignment.subject_id), None)
            if invalid_subject:
                return Response({"code": 400, "info": "试卷中的题目与科目不匹配"})
            preset_questions = ordered_questions
            score_overrides = {question.id: assignment.per_question_score for question in ordered_questions}

        try:
            attempt, question_payload, expires_at, remaining = create_attempt_with_questions(
                user=request.user,
                subject=assignment.subject,
                question_type=assignment.question_type,
                size=assignment.question_count,
                duration_seconds=assignment.duration_seconds,
                mode="exam",
                assignment=assignment,
                preset_questions=preset_questions,
                score_overrides=score_overrides,
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
            is_review_required=True,
            status__in=["completed", "expired"],
        ).select_related("user", "subject", "assignment").order_by("-submitted_at")

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
            is_review_required=True,
            status__in=["completed", "expired"],
        ).select_related("user", "subject", "assignment").order_by("-submitted_at")

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


class TeacherDashboardOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if getattr(request.user, "role", "") != "teacher":
            return Response({"code": 403, "info": "仅教师可操作"})

        user = request.user
        question_qs = Question.objects.filter(created_by=user)
        question_stats = question_qs.aggregate(
            total=Count("id"),
            objective=Count("id", filter=Q(question_type="objective")),
            subjective=Count("id", filter=Q(question_type="subjective")),
        )
        subject_rows = (
            question_qs.values("subject_id", "subject__name")
            .annotate(
                total=Count("id"),
                objective=Count("id", filter=Q(question_type="objective")),
                subjective=Count("id", filter=Q(question_type="subjective")),
                last_updated=Max("updated_at"),
            )
            .order_by("-last_updated", "subject__name")
        )
        question_subjects = [
            {
                "subject_id": row["subject_id"],
                "subject_name": row["subject__name"],
                "total": row["total"],
                "objective": row["objective"],
                "subjective": row["subjective"],
                "last_updated": row["last_updated"],
            }
            for row in subject_rows
        ]

        assignment_qs = (
            ExamAssignment.objects.filter(created_by=user)
            .select_related("subject")
            .annotate(
                total_attempts=Count("attempts", distinct=True),
                pending_reviews=Count(
                    "attempts",
                    filter=Q(
                        attempts__is_review_required=True,
                        attempts__status__in=["completed", "expired"],
                    ),
                    distinct=True,
                ),
            )
            .order_by("start_time")
        )
        assignment_list = list(assignment_qs)

        status_counts = {"draft": 0, "published": 0, "closed": 0}
        phase_counts = {"upcoming": 0, "ongoing": 0, "ended": 0}
        subject_assignment_map: Dict[int, Dict[str, object]] = {}
        recent_assignments = []

        for assignment in assignment_list:
            status_counts[assignment.status] = status_counts.get(assignment.status, 0) + 1
            phase = assignment.phase
            if phase in phase_counts:
                phase_counts[phase] += 1
            subject_entry = subject_assignment_map.setdefault(
                assignment.subject_id or 0,
                {
                    "subject_id": assignment.subject_id,
                    "subject_name": assignment.subject.name if assignment.subject else "未分类",
                    "total": 0,
                    "upcoming": 0,
                    "ongoing": 0,
                    "ended": 0,
                },
            )
            subject_entry["total"] += 1
            if phase in subject_entry:
                subject_entry[phase] += 1

        for assignment in assignment_list[:5]:
            recent_assignments.append({
                "id": assignment.id,
                "title": assignment.title,
                "subject_name": assignment.subject.name if assignment.subject else "",
                "phase": assignment.phase,
                "status": assignment.status,
                "start_time": assignment.start_time,
                "end_time": assignment.end_time,
                "total_attempts": getattr(assignment, "total_attempts", 0),
                "pending_reviews": getattr(assignment, "pending_reviews", 0),
            })

        pending_qs = PracticeAttempt.objects.filter(
            is_review_required=True,
            status__in=["completed", "expired"],
        ).select_related("user", "subject", "assignment").order_by("-submitted_at")
        pending_total = pending_qs.count()
        pending_items = [
            {
                "id": attempt.id,
                "student_name": attempt.user.username,
                "subject_name": attempt.subject.name,
                "assignment_id": attempt.assignment_id,
                "assignment_title": attempt.assignment.title if attempt.assignment else None,
                "submitted_at": attempt.submitted_at,
                "mode": attempt.mode,
                "question_type": attempt.question_type,
            }
            for attempt in pending_qs[:5]
        ]

        payload = {
            "question_stats": {
                "total": question_stats.get("total", 0),
                "objective": question_stats.get("objective", 0),
                "subjective": question_stats.get("subjective", 0),
                "subjects": question_subjects,
            },
            "assignment_stats": {
                "total": len(assignment_list),
                "status": status_counts,
                "phase": phase_counts,
                "subjects": sorted(subject_assignment_map.values(), key=lambda item: item["total"], reverse=True),
                "recent": recent_assignments,
            },
            "pending_reviews": {
                "total": pending_total,
                "items": pending_items,
            },
        }

        return Response({"code": 200, "info": "获取教师概览成功", "data": payload})


class StudentDashboardOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if getattr(request.user, "role", "") != "student":
            return Response({"code": 403, "info": "仅学生可操作"})

        user = request.user
        now = timezone.now()

        assignments_list = list(
            ExamAssignment.objects.filter(status="published")
            .select_related("subject")
            .order_by("start_time")
        )
        assignment_ids = [assignment.id for assignment in assignments_list]

        attempt_map: Dict[int, PracticeAttempt] = {}
        attempts_qs = (
            PracticeAttempt.objects.filter(user=user, assignment_id__in=assignment_ids)
            .select_related("assignment")
            .order_by("-started_at")
        )
        for attempt in attempts_qs:
            if attempt.assignment_id and attempt.assignment_id not in attempt_map:
                attempt_map[attempt.assignment_id] = attempt

        completed_statuses = {"completed", "expired"}
        phase_counts = {"upcoming": 0, "ongoing": 0, "ended": 0, "completed": 0}
        def bump_phase(key: str):
            phase_counts[key] = phase_counts.get(key, 0) + 1

        for assignment in assignments_list:
            attempt = attempt_map.get(assignment.id)
            if attempt and attempt.status in completed_statuses:
                bump_phase("completed")
            else:
                bump_phase(assignment.phase)

        sorted_assignments = sorted(
            assignments_list,
            key=lambda item: (
                0 if item.phase == "ongoing" else (1 if item.phase == "upcoming" else 2),
                item.start_time,
            ),
        )
        assignment_preview = []
        for assignment in sorted_assignments:
            attempt = attempt_map.get(assignment.id)
            student_phase = assignment.phase
            if attempt and attempt.status in completed_statuses:
                student_phase = "completed"
            assignment_preview.append({
                "id": assignment.id,
                "title": assignment.title,
                "subject_name": assignment.subject.name if assignment.subject else "",
                "phase": assignment.phase,
                "student_phase": student_phase,
                "start_time": assignment.start_time,
                "end_time": assignment.end_time,
                "duration_seconds": assignment.duration_seconds,
                "attempt_status": attempt.status if attempt else None,
                "attempt_id": attempt.id if attempt else None,
            })
            if len(assignment_preview) >= 5:
                break

        practice_qs = PracticeAttempt.objects.filter(user=user)
        practice_total = practice_qs.count()
        practice_completed = practice_qs.filter(status__in=["completed", "expired"]).count()
        practice_ongoing = practice_qs.filter(status="ongoing").count()

        window_start = now - timedelta(days=6)
        recent_map = {
            item["day"]: item["count"]
            for item in (
                practice_qs.filter(submitted_at__isnull=False, submitted_at__gte=window_start)
                .annotate(day=TruncDate("submitted_at"))
                .values("day")
                .annotate(count=Count("id"))
            )
        }
        trend_payload = []
        recent_completed = 0
        for offset in range(6, -1, -1):
            day = (now - timedelta(days=offset)).date()
            count = recent_map.get(day, 0)
            trend_payload.append({"date": day, "count": count})
            recent_completed += count

        progress_percent = 0
        if recent_completed:
            progress_percent = min(100, int((recent_completed / 7) * 100))

        wrong_book_count = WrongBookEntry.objects.filter(user=user).count()
        pending_reviews = practice_qs.filter(
            is_review_required=True,
            status__in=["completed", "expired"],
        ).count()

        payload = {
            "exam_stats": {
                "ongoing": phase_counts["ongoing"],
                "upcoming": phase_counts["upcoming"],
                "ended": phase_counts["ended"],
                "recent": assignment_preview,
            },
            "practice_stats": {
                "total": practice_total,
                "completed": practice_completed,
                "ongoing": practice_ongoing,
                "recent_completed": recent_completed,
                "trend": trend_payload,
                "progress_percent": progress_percent,
            },
            "wrong_book_count": wrong_book_count,
            "pending_reviews": pending_reviews,
        }

        return Response({"code": 200, "info": "获取学生概览成功", "data": payload})


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
            context={"force_show_solution": True},
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
            if not attempt.is_review_required:
                return Response({"code": 400, "info": "该试卷无需批阅"})

            item_payload = request.data.get("items", [])
            if not isinstance(item_payload, list) or not item_payload:
                return Response({"code": 400, "info": "请提交题目得分"})

            all_items = list(attempt.items.select_related("question"))
            if not all_items:
                return Response({"code": 400, "info": "试卷题目数据缺失"})

            subjective_items = [item for item in all_items if item.question.question_type == "subjective"]
            if not subjective_items:
                return Response({"code": 400, "info": "该试卷无需批阅"})

            item_map = {item.id: item for item in subjective_items}
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
                max_score = item.expected_score or resolve_score(item.question.question_type, item.question.score)
                clamped_score = max(0, min(raw_score, max_score))
                if item.awarded_score != clamped_score:
                    item.awarded_score = clamped_score
                    updated_items.append(item)

            if not provided_ids:
                return Response({"code": 400, "info": "请至少为一道题设置得分"})

            if updated_items:
                PracticeAttemptItem.objects.bulk_update(updated_items, ["awarded_score"])

            total_obtained = sum(item.awarded_score for item in all_items)
            total_possible = sum(
                item.expected_score or resolve_score(item.question.question_type, item.question.score)
                for item in all_items
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
            context={"force_show_solution": True},
        )
        return Response({
            "code": 200,
            "info": "批阅完成",
            "data": {
                "attempt": serializer.data,
                "items": item_serializer.data,
            },
        })
