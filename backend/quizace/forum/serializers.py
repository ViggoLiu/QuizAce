from rest_framework import serializers
from .models import ForumComment, CommentLike, CommentReply, Notification, ResourceComment
from user.models import SysUser


class UserSerializer(serializers.ModelSerializer):
    """
    用户序列化器，用于嵌套显示用户信息
    """
    class Meta:
        model = SysUser
        fields = ['id', 'username', 'avatar', 'role']


class CommentReplySerializer(serializers.ModelSerializer):
    """
    评论回复序列化器
    """
    user = UserSerializer(read_only=True)
    to_user = UserSerializer(read_only=True)
    to_user_id = serializers.IntegerField(write_only=True, required=True, help_text="回复对象用户ID")

    class Meta:
        model = CommentReply
        fields = ['id', 'user', 'to_user', 'to_user_id', 'content', 'parent_reply', 'create_time']
        extra_kwargs = {
            'parent_reply': {'write_only': True}
        }


class ForumCommentSerializer(serializers.ModelSerializer):
    """
    论坛评论序列化器
    """
    user = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField(read_only=True)
    is_liked = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ForumComment
        fields = ['id', 'user', 'content', 'like_count', 'reply_count', 'is_liked', 'replies', 'create_time']

    def get_replies(self, obj):
        """
        获取评论的一级回复
        """
        # 只获取直接回复（parent_reply为None）
        replies = obj.replies.filter(parent_reply__isnull=True, is_deleted=False)
        return CommentReplySerializer(replies, many=True).data

    def get_is_liked(self, obj):
        """
        检查当前用户是否已点赞
        """
        user = self.context.get('request').user
        if user and user.is_authenticated:
            return obj.likes.filter(user=user).exists()
        return False


class NotificationSerializer(serializers.ModelSerializer):
    """
    消息通知序列化器
    """
    class Meta:
        model = Notification
        fields = ['id', 'type', 'content', 'is_read', 'create_time']


class ResourceCommentSerializer(serializers.ModelSerializer):
    """
    学习资源评论序列化器
    """
    user = UserSerializer(read_only=True)
    is_liked = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ResourceComment
        fields = ['id', 'user', 'content', 'rating', 'like_count', 'is_liked', 'create_time']

    def get_is_liked(self, obj):
        """
        检查当前用户是否已点赞
        """
        user = self.context.get('request').user
        if user and user.is_authenticated:
            return obj.likes.filter(user=user).exists()
        return False


class ResourceCommentCreateSerializer(serializers.ModelSerializer):
    """
    学习资源评论创建序列化器
    """
    class Meta:
        model = ResourceComment
        fields = ['content', 'rating']

    def validate_rating(self, value):
        """
        验证评分范围
        """
        if value < 1 or value > 5:
            raise serializers.ValidationError("评分必须在1-5之间")
        return value


class CommentLikeSerializer(serializers.ModelSerializer):
    """
    评论点赞序列化器
    """
    class Meta:
        model = CommentLike
        fields = ['id', 'comment', 'user', 'create_time']
        read_only_fields = ['user', 'create_time']
