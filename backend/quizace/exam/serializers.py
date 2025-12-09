import json

from rest_framework import serializers

from .constants import resolve_score
from .models import (
    ExamAssignment,
    PracticeAttempt,
    PracticeAttemptItem,
    Question,
    QuestionDraft,
    Subject,
    WrongBookEntry,
)


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ("id", "name", "description")


class QuestionSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    options = serializers.SerializerMethodField()
    media_url = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = (
            "id",
            "subject",
            "subject_name",
            "question_type",
            "source_mode",
            "status",
            "content",
            "options",
            "answer",
            "analysis",
            "score",
            "media_url",
            "created_by",
            "metadata",
        )

    def get_options(self, obj):
        return obj.options_dict

    def get_media_url(self, obj):
        return obj.media_url or ""


class QuestionCreateSerializer(serializers.ModelSerializer):
    options = serializers.JSONField(required=False, allow_null=True)

    class Meta:
        model = Question
        fields = (
            "subject",
            "question_type",
            "content",
            "options",
            "answer",
            "analysis",
            "score",
            "source_mode",
            "status",
            "media_url",
            "metadata",
        )
        extra_kwargs = {
            "analysis": {"required": False, "allow_blank": True},
            "score": {"required": False},
            "metadata": {"required": False},
            "media_url": {"required": False, "allow_blank": True},
        }

    def validate(self, attrs):
        question_type = attrs.get("question_type")
        options = attrs.get("options")
        if question_type == "objective" and not options:
            raise serializers.ValidationError("客观题至少需要提供选项信息")
        if question_type == "objective" and not attrs.get("answer"):
            raise serializers.ValidationError("客观题需要设置标准答案")
        score = attrs.get("score")
        if not score:
            attrs["score"] = resolve_score(question_type, None)
        return attrs

    def _normalize_options(self, value):
        if value is None:
            return None
        if isinstance(value, dict):
            return value
        if isinstance(value, list):
            normalized = {}
            for index, item in enumerate(value):
                label = chr(ord("A") + index)
                if isinstance(item, dict):
                    text = item.get("text") or item.get("value") or item.get("label") or ""
                    normalized[item.get("label") or label] = text
                else:
                    normalized[label] = str(item)
            return normalized
        raise serializers.ValidationError("选项格式不正确")

    def create(self, validated_data):
        options = validated_data.pop("options", None)
        normalized = self._normalize_options(options)
        if normalized is not None:
            validated_data["options"] = json.dumps(normalized, ensure_ascii=False)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        options = validated_data.pop("options", None)
        if options is not None:
            validated_data["options"] = json.dumps(self._normalize_options(options), ensure_ascii=False)
        return super().update(instance, validated_data)


class PracticeQuestionSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    options = serializers.SerializerMethodField()
    score = serializers.SerializerMethodField()
    media_url = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ("id", "question_type", "content", "options", "score", "subject_name", "media_url")

    def get_options(self, obj):
        return obj.options_dict

    def get_score(self, obj):
        return resolve_score(obj.question_type, obj.score)

    def get_media_url(self, obj):
        return obj.media_url or ""


class PracticeAttemptItemSerializer(serializers.ModelSerializer):
    question = serializers.SerializerMethodField()
    in_wrong_book = serializers.SerializerMethodField()

    class Meta:
        model = PracticeAttemptItem
        fields = ("id", "order", "question", "user_answer", "is_correct", "awarded_score", "in_wrong_book")

    def get_question(self, obj):
        question = obj.question
        force_show = self.context.get("force_show_solution", False)
        visibility = self.context.get("solution_visibility") or {}
        data = {
            "id": question.id,
            "question_type": question.question_type,
            "content": question.content,
            "options": question.options_dict,
            "score": obj.expected_score or resolve_score(question.question_type, question.score),
            "subject_name": question.subject.name,
            "media_url": question.media_url or "",
        }
        can_show = force_show or visibility.get(question.question_type)
        if can_show:
            data["answer"] = question.answer
            data["analysis"] = question.analysis
        return data

    def get_in_wrong_book(self, obj):
        question_ids = self.context.get("wrong_question_ids")
        if not question_ids:
            return False
        return obj.question_id in question_ids


class PracticeAttemptSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    user_name = serializers.CharField(source="user.username", read_only=True)
    assignment_title = serializers.CharField(source="assignment.title", read_only=True)

    class Meta:
        model = PracticeAttempt
        fields = (
            "id",
            "mode",
            "subject",
            "subject_name",
            "question_type",
            "duration_seconds",
            "total_questions",
            "correct_count",
            "total_score",
            "obtained_score",
            "status",
            "is_review_required",
            "started_at",
            "submitted_at",
            "assignment",
            "assignment_title",
            "user_name",
            "review_comment",
            "reviewed_at",
        )


class ExamAssignmentSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    created_by_name = serializers.CharField(source="created_by.username", read_only=True)
    phase = serializers.SerializerMethodField()

    class Meta:
        model = ExamAssignment
        fields = (
            "id",
            "title",
            "subject",
            "subject_name",
            "question_type",
            "question_count",
            "duration_seconds",
            "start_time",
            "end_time",
            "status",
            "phase",
            "description",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        )

    def get_phase(self, obj):
        return obj.phase


class WrongBookEntrySerializer(serializers.ModelSerializer):
    question = QuestionSerializer(read_only=True)
    subject_id = serializers.IntegerField(source="subject.id", read_only=True)
    subject_name = serializers.CharField(source="subject.name", read_only=True)

    class Meta:
        model = WrongBookEntry
        fields = (
            "id",
            "subject_id",
            "subject_name",
            "question",
            "last_user_answer",
            "wrong_times",
            "last_wrong_at",
            "created_at",
        )


class QuestionDraftSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    teacher_name = serializers.CharField(source="teacher.username", read_only=True)
    media_url = serializers.SerializerMethodField()
    question_id = serializers.IntegerField(source="question.id", read_only=True)

    class Meta:
        model = QuestionDraft
        fields = (
            "id",
            "teacher",
            "teacher_name",
            "subject",
            "subject_name",
            "question_type",
            "source_mode",
            "status",
            "media_url",
            "parsed_title",
            "parsed_content",
            "parsed_options",
            "parsed_answer",
            "parsed_analysis",
            "error_message",
            "question_id",
            "created_at",
            "updated_at",
        )

    def get_media_url(self, obj):
        return obj.resolved_media_url
