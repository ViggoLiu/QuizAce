from django.db import models
from django.conf import settings
from django.utils import timezone
from rest_framework import serializers
from learning_resource.models import LearningResource


class ForumComment(models.Model):
    """
    论坛评论模型
    """
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="forum_comments",
        verbose_name="评论用户"
    )
    content = models.TextField(verbose_name="评论内容")
    like_count = models.IntegerField(default=0, verbose_name="点赞数")
    reply_count = models.IntegerField(default=0, verbose_name="回复数")
    is_deleted = models.BooleanField(default=False, verbose_name="是否删除")
    deleted_reason = models.CharField(max_length=255, null=True, blank=True, verbose_name="删除原因")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "forum_comment"
        verbose_name = "论坛评论"
        verbose_name_plural = verbose_name
        ordering = ['-create_time']  # 按创建时间倒序排列

    def __str__(self):
        return f"{self.user.username}: {self.content[:20]}"


class CommentLike(models.Model):
    """
    评论点赞模型
    """
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comment_likes",
        verbose_name="点赞用户"
    )
    comment = models.ForeignKey(
        ForumComment,
        on_delete=models.CASCADE,
        related_name="likes",
        verbose_name="被点赞评论"
    )
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="点赞时间")

    class Meta:
        db_table = "comment_like"
        verbose_name = "评论点赞"
        verbose_name_plural = verbose_name
        unique_together = ('user', 'comment')  # 确保一个用户只能点赞一次


class CommentReply(models.Model):
    """
    评论回复模型，支持多级回复
    """
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comment_replies",
        verbose_name="回复用户"
    )
    comment = models.ForeignKey(
        ForumComment,
        on_delete=models.CASCADE,
        related_name="replies",
        verbose_name="所属评论"
    )
    parent_reply = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="child_replies",
        verbose_name="父回复"
    )
    content = models.TextField(verbose_name="回复内容")
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_replies",
        verbose_name="回复对象"
    )
    is_deleted = models.BooleanField(default=False, verbose_name="是否删除")
    deleted_reason = models.CharField(max_length=255, null=True, blank=True, verbose_name="删除原因")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="回复时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "comment_reply"
        verbose_name = "评论回复"
        verbose_name_plural = verbose_name
        ordering = ['create_time']  # 按创建时间正序排列

    def __str__(self):
        return f"{self.user.username} -> {self.to_user.username}: {self.content[:20]}"


class Notification(models.Model):
    """
    消息通知模型
    """
    NOTIFICATION_TYPES = (
        ('comment_deleted', '评论被删除'),
        ('user_banned', '用户被禁言'),
        ('system_notice', '系统通知'),
    )

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name="接收用户"
    )
    type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES, verbose_name="通知类型")
    content = models.TextField(verbose_name="通知内容")
    is_read = models.BooleanField(default=False, verbose_name="是否已读")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = "notification"
        verbose_name = "消息通知"
        verbose_name_plural = verbose_name
        ordering = ['-create_time']  # 按创建时间倒序排列

    def __str__(self):
        return f"{self.get_type_display()} - {self.content[:20]}"


class ResourceComment(models.Model):
    """
    学习资源评论打分模型
    """
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="resource_comments",
        verbose_name="评论用户"
    )
    resource = models.ForeignKey(
        LearningResource,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="所属资源"
    )
    content = models.TextField(verbose_name="评论内容")
    rating = models.IntegerField(verbose_name="评分", choices=[(i, i) for i in range(1, 6)])  # 1-5分
    like_count = models.IntegerField(default=0, verbose_name="点赞数")
    is_deleted = models.BooleanField(default=False, verbose_name="是否删除")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "resource_comment"
        verbose_name = "学习资源评论"
        verbose_name_plural = verbose_name
        ordering = ['-create_time']  # 按创建时间倒序排列

    def __str__(self):
        return f"{self.user.username}: {self.content[:20]} (评分: {self.rating})"


class ResourceCommentLike(models.Model):
    """
    学习资源评论点赞模型
    """
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="resource_comment_likes",
        verbose_name="点赞用户"
    )
    resource_comment = models.ForeignKey(
        ResourceComment,
        on_delete=models.CASCADE,
        related_name="likes",
        verbose_name="被点赞资源评论"
    )
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="点赞时间")

    class Meta:
        db_table = "resource_comment_like"
        verbose_name = "学习资源评论点赞"
        verbose_name_plural = verbose_name
        unique_together = ('user', 'resource_comment')  # 确保一个用户只能点赞一次
