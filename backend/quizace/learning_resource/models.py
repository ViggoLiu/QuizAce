from django.db import models
from django.conf import settings
from rest_framework import serializers


class LearningResource(models.Model):

    STATUS_CHOICES = (
        (0, "审核中"),
        (1, "已通过"),
        (2, "已拒绝"),
    )

    ROLE_CHOICES = (
        ('student', '学生'),
        ('teacher', '老师')
    )

    id = models.AutoField(primary_key=True)

    # 基本信息
    name = models.CharField(max_length=255, verbose_name="资源名称")
    course = models.CharField(max_length=100, verbose_name="所属课程")
    college = models.CharField(max_length=100, verbose_name="所属学院")

    description = models.TextField(null=True, blank=True, verbose_name="资源简介")
    file = models.FileField(upload_to='learning_resource/', verbose_name="资源文件", null=True, blank=True)
    file_size = models.CharField(max_length=50, null=True, blank=True)
    file_type = models.CharField(max_length=20, null=True, blank=True)

    # 用户信息
    uploader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="uploaded_resources",
        verbose_name="上传人"
    )

    uploader_role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    # 数据统计
    click_count = models.IntegerField(default=0)
    download_count = models.IntegerField(default=0)
    favorite_count = models.IntegerField(default=0)

    # 审核信息
    status = models.IntegerField(default=0, choices=STATUS_CHOICES)
    reject_reason = models.CharField(max_length=255, null=True, blank=True)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "learning_resource"
        verbose_name = "学习资源"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class ResourceClickRecord(models.Model):
    """
    用户点击记录模型，限制短时间内重复点击
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="click_records",
        verbose_name="用户"
    )
    resource = models.ForeignKey(
        LearningResource,
        on_delete=models.CASCADE,
        related_name="click_records",
        verbose_name="资源"
    )
    clicked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "resource_click_record"
        verbose_name = "资源点击记录"
        verbose_name_plural = verbose_name
        # 按用户和资源创建索引，提高查询效率
        indexes = [
            models.Index(fields=['user', 'resource']),
        ]


class ResourceFavorite(models.Model):
    """
    用户收藏关系模型，实现用户与资源的多对多关系
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="用户"
    )
    resource = models.ForeignKey(
        LearningResource,
        on_delete=models.CASCADE,
        related_name="favorited_by",
        verbose_name="资源"
    )
    favorited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "resource_favorite"
        verbose_name = "资源收藏"
        verbose_name_plural = verbose_name
        # 联合唯一约束，确保同一用户只能收藏一次同一资源
        unique_together = ('user', 'resource')


class LearningResourceSerializer(serializers.ModelSerializer):
    uploader_name = serializers.CharField(source="uploader.username", read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    file_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = LearningResource
        # 明确列出所有需要的字段，排除file字段
        exclude = ('file',)

    def get_is_favorited(self, obj):
        """
        检查当前用户是否已收藏该资源
        """
        user = self.context.get('request').user
        if user and user.is_authenticated:
            return ResourceFavorite.objects.filter(user=user, resource=obj).exists()
        return False

    def get_file_url(self, obj):
        """
        获取文件的完整URL
        """
        if obj.file and hasattr(obj.file, 'url'):
            return self.context['request'].build_absolute_uri(obj.file.url)
        return None