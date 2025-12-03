from django.contrib import admin

from .models import PracticeAttempt, PracticeAttemptItem, Question, Subject


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "subject", "question_type", "score", "created_at")
    list_filter = ("question_type", "subject")
    search_fields = ("content",)
    autocomplete_fields = ("subject",)


@admin.register(PracticeAttempt)
class PracticeAttemptAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "subject", "question_type", "status", "correct_count", "total_questions")
    list_filter = ("question_type", "status", "subject")
    search_fields = ("user__username",)
    autocomplete_fields = ("user", "subject")


@admin.register(PracticeAttemptItem)
class PracticeAttemptItemAdmin(admin.ModelAdmin):
    list_display = ("id", "attempt", "question", "order", "is_correct")
    list_filter = ("attempt__question_type",)
    search_fields = ("question__content",)
    autocomplete_fields = ("attempt", "question")
