from rest_framework import serializers

from .constants import resolve_score
from .models import ExamAssignment, PracticeAttempt, PracticeAttemptItem, Question, Subject, WrongBookEntry


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ("id", "name", "description")


class QuestionSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    options = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = (
            "id",
            "subject",
            "subject_name",
            "question_type",
            "content",
            "options",
            "answer",
            "analysis",
            "score",
        )

    def get_options(self, obj):
        return obj.options_dict


class PracticeQuestionSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    options = serializers.SerializerMethodField()
    score = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ("id", "question_type", "content", "options", "score", "subject_name")

    def get_options(self, obj):
        return obj.options_dict

    def get_score(self, obj):
        return resolve_score(obj.question_type, obj.score)


class PracticeAttemptItemSerializer(serializers.ModelSerializer):
    question = serializers.SerializerMethodField()
    in_wrong_book = serializers.SerializerMethodField()

    class Meta:
        model = PracticeAttemptItem
        fields = ("id", "order", "question", "user_answer", "is_correct", "awarded_score", "in_wrong_book")

    def get_question(self, obj):
        question = obj.question
        show_solution = self.context.get("show_solution", False)
        data = {
            "id": question.id,
            "question_type": question.question_type,
            "content": question.content,
            "options": question.options_dict,
            "score": resolve_score(question.question_type, question.score),
            "subject_name": question.subject.name,
        }
        if show_solution:
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
