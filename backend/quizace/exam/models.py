import json

from django.conf import settings
from django.db import models
from django.utils import timezone

QUESTION_SOURCE_CHOICES = (
    ("ocr", "OCR解析"),
    ("manual", "手动录入"),
)

QUESTION_STATUS_CHOICES = (
    ("draft", "草稿"),
    ("ready", "可用"),
    ("archived", "已归档"),
)

QUESTION_TYPE_CHOICES = (
    ("objective", "客观题"),
    ("subjective", "主观题"),
)

ATTEMPT_TYPE_CHOICES = QUESTION_TYPE_CHOICES + (("mixed", "综合试卷"),)

QUESTION_DRAFT_STATUS_CHOICES = (
    ("uploaded", "已上传"),
    ("processing", "解析中"),
    ("parsed", "解析完成"),
    ("failed", "解析失败"),
    ("published", "已发布"),
)


class Subject(models.Model):
    """课程科目，用于对题目进行归类。"""

    name = models.CharField(max_length=64, unique=True, verbose_name="科目名称")
    description = models.TextField(blank=True, verbose_name="简介")

    class Meta:
        db_table = "exam_subject"
        verbose_name = "科目"
        verbose_name_plural = verbose_name

    def __str__(self) -> str:
        return self.name


class Question(models.Model):
    """题目模型，支持客观题与主观题。"""

    QUESTION_TYPES = QUESTION_TYPE_CHOICES

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="questions", verbose_name="所属科目")
    question_type = models.CharField(max_length=16, choices=QUESTION_TYPE_CHOICES, default="objective", verbose_name="题目类型")
    source_mode = models.CharField(max_length=16, choices=QUESTION_SOURCE_CHOICES, default="manual", verbose_name="录入方式")
    status = models.CharField(max_length=16, choices=QUESTION_STATUS_CHOICES, default="ready", verbose_name="状态")
    content = models.TextField(verbose_name="题干")
    options = models.TextField(blank=True, null=True, verbose_name="客观题选项(JSON文本)")
    answer = models.TextField(verbose_name="参考答案")
    analysis = models.TextField(blank=True, null=True, verbose_name="解析")
    score = models.PositiveIntegerField(default=5, verbose_name="分值")
    media_url = models.CharField(max_length=255, blank=True, null=True, verbose_name="题干图片地址")
    metadata = models.JSONField(default=dict, blank=True, verbose_name="扩展信息")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_questions",
        verbose_name="录入教师",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "exam_question"
        verbose_name = "题目"
        verbose_name_plural = verbose_name

    def __str__(self) -> str:
        return f"[{self.get_question_type_display()}]{self.content[:20]}"

    @property
    def options_dict(self):
        if not self.options:
            return None
        try:
            return json.loads(self.options)
        except json.JSONDecodeError:
            return None


class QuestionDraft(models.Model):
    """教师上传题目的草稿，支持 OCR 与手动录入。"""

    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="question_drafts",
        verbose_name="上传教师",
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="question_drafts",
        verbose_name="科目",
    )
    question_type = models.CharField(max_length=16, choices=Question.QUESTION_TYPES, verbose_name="题目类型")
    source_mode = models.CharField(max_length=16, choices=QUESTION_SOURCE_CHOICES, default="manual", verbose_name="来源模式")
    status = models.CharField(max_length=16, choices=QUESTION_DRAFT_STATUS_CHOICES, default="uploaded", verbose_name="处理状态")
    media = models.FileField(upload_to="exam/questions/", blank=True, null=True, verbose_name="题干文件")
    media_url = models.CharField(max_length=255, blank=True, verbose_name="题干文件地址")
    parsed_title = models.CharField(max_length=255, blank=True, verbose_name="解析标题")
    parsed_content = models.TextField(blank=True, verbose_name="解析题干")
    parsed_options = models.JSONField(default=list, blank=True, verbose_name="解析选项")
    parsed_answer = models.TextField(blank=True, verbose_name="解析答案")
    parsed_analysis = models.TextField(blank=True, verbose_name="解析说明")
    error_message = models.TextField(blank=True, verbose_name="解析错误信息")
    question = models.OneToOneField(
        Question,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="draft",
        verbose_name="发布后的题目",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "exam_question_draft"
        verbose_name = "题目草稿"
        verbose_name_plural = verbose_name
        ordering = ("-updated_at", "-id")

    def __str__(self) -> str:
        return f"{self.teacher} - {self.get_status_display()}"

    @property
    def resolved_media_url(self) -> str:
        if self.media and hasattr(self.media, "url"):
            return self.media.url
        return self.media_url or ""


class ExamAssignment(models.Model):
    """教师发布的正式考试任务"""

    STATUS_CHOICES = (
        ("draft", "草稿"),
        ("published", "已发布"),
        ("closed", "已结束"),
    )

    title = models.CharField(max_length=128, verbose_name="考试标题")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="assignments", verbose_name="科目")
    question_type = models.CharField(max_length=16, choices=ATTEMPT_TYPE_CHOICES, verbose_name="题型")
    question_count = models.PositiveIntegerField(default=10, verbose_name="题目数量")
    duration_seconds = models.PositiveIntegerField(default=1800, verbose_name="考试时长(秒)")
    start_time = models.DateTimeField(verbose_name="开始时间")
    end_time = models.DateTimeField(verbose_name="结束时间")
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="published", verbose_name="状态")
    description = models.TextField(blank=True, verbose_name="说明")
    question_ids = models.JSONField(default=list, blank=True, verbose_name="固定题目列表")
    per_question_score = models.PositiveIntegerField(default=10, verbose_name="单题分值")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_assignments",
        verbose_name="发布教师",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "exam_assignment"
        verbose_name = "考试任务"
        verbose_name_plural = verbose_name
        ordering = ("-start_time", "-id")

    def __str__(self) -> str:
        return self.title

    @property
    def phase(self) -> str:
        """返回当前时间段状态: upcoming/ongoing/ended"""
        now = timezone.now()
        if now < self.start_time:
            return "upcoming"
        if now > self.end_time:
            return "ended"
        return "ongoing"


class PracticeAttempt(models.Model):
    """学生一次模拟练习/考试记录"""

    STATUS_CHOICES = (
        ("ongoing", "进行中"),
        ("completed", "已完成"),
        ("expired", "已过期"),
    )

    MODE_CHOICES = (
        ("practice", "练习"),
        ("exam", "考试"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="practice_attempts",
        verbose_name="学生",
    )
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name="科目")
    question_type = models.CharField(max_length=16, choices=ATTEMPT_TYPE_CHOICES, verbose_name="题型")
    duration_seconds = models.PositiveIntegerField(default=1800, verbose_name="限时(秒)")
    total_questions = models.PositiveIntegerField(default=0, verbose_name="题目数量")
    correct_count = models.PositiveIntegerField(default=0, verbose_name="客观题正确数")
    total_score = models.PositiveIntegerField(default=0, verbose_name="总分")
    obtained_score = models.PositiveIntegerField(default=0, verbose_name="得分")
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="ongoing", verbose_name="状态")
    is_review_required = models.BooleanField(default=False, verbose_name="待教师批阅")
    started_at = models.DateTimeField(auto_now_add=True, verbose_name="开始时间")
    submitted_at = models.DateTimeField(null=True, blank=True, verbose_name="提交时间")
    mode = models.CharField(max_length=16, choices=MODE_CHOICES, default="practice", verbose_name="来源类型")
    assignment = models.ForeignKey(
        ExamAssignment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="attempts",
        verbose_name="关联考试",
    )
    review_comment = models.TextField(blank=True, null=True, verbose_name="教师评语")
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_attempts",
        verbose_name="批阅教师",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name="批阅时间")

    class Meta:
        db_table = "exam_practice_attempt"
        verbose_name = "练习记录"
        verbose_name_plural = verbose_name

    def __str__(self) -> str:
        return f"{self.user} {self.subject} {self.question_type} {self.mode}"


class PracticeAttemptItem(models.Model):
    """练习中的单题作答"""

    attempt = models.ForeignKey(
        PracticeAttempt,
        related_name="items",
        on_delete=models.CASCADE,
        verbose_name="练习记录",
    )
    question = models.ForeignKey(Question, on_delete=models.PROTECT, verbose_name="题目")
    order = models.PositiveIntegerField(default=1, verbose_name="题目顺序")
    user_answer = models.TextField(blank=True, null=True, verbose_name="学生答案")
    is_correct = models.BooleanField(null=True, blank=True, verbose_name="是否正确")
    awarded_score = models.PositiveIntegerField(default=0, verbose_name="得分")
    expected_score = models.PositiveIntegerField(default=0, verbose_name="题目分值")

    class Meta:
        db_table = "exam_practice_attempt_item"
        verbose_name = "练习题目记录"
        verbose_name_plural = verbose_name
        ordering = ("order", "id")

    def __str__(self) -> str:
        return f"Attempt {self.attempt_id} - Q{self.order}"


class WrongBookEntry(models.Model):
    """学生错题本中的题目记录。"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wrong_book_entries",
        verbose_name="学生",
    )
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name="科目")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name="题目")
    last_attempt = models.ForeignKey(
        PracticeAttempt,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="wrong_book_entries",
        verbose_name="最近关联练习",
    )
    last_attempt_item = models.ForeignKey(
        PracticeAttemptItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="wrong_book_entries",
        verbose_name="最近关联作答",
    )
    last_user_answer = models.TextField(blank=True, verbose_name="最近答案")
    wrong_times = models.PositiveIntegerField(default=1, verbose_name="累计错误次数")
    last_wrong_at = models.DateTimeField(auto_now=True, verbose_name="最后错误时间")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = "exam_wrong_book_entry"
        verbose_name = "错题本记录"
        verbose_name_plural = verbose_name
        unique_together = ("user", "question")
        ordering = ("-last_wrong_at", "-id")

    def __str__(self) -> str:
        return f"{self.user} - {self.question}"
