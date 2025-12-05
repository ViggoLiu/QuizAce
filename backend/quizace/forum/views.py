from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import ForumComment, CommentLike, CommentReply, Notification, ResourceComment, ResourceCommentLike
from .serializers import (
    ForumCommentSerializer,
    CommentLikeSerializer,
    CommentReplySerializer,
    NotificationSerializer,
    ResourceCommentSerializer,
    ResourceCommentCreateSerializer
)
from user.models import SysUser


class ForumCommentViewSet(viewsets.ModelViewSet):
    """
    论坛评论视图集
    """
    queryset = ForumComment.objects.filter(is_deleted=False)
    serializer_class = ForumCommentSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """
        创建新评论
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        """
        点赞/取消点赞
        """
        comment = self.get_object()
        user = request.user
        like, created = CommentLike.objects.get_or_create(comment=comment, user=user)

        if created:
            # 新增点赞
            comment.like_count += 1
            comment.save()
            return Response({'status': 'liked', 'like_count': comment.like_count})
        else:
            # 取消点赞
            like.delete()
            comment.like_count -= 1
            comment.save()
            return Response({'status': 'unliked', 'like_count': comment.like_count})

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def replies(self, request, pk=None):
        """
        获取评论的所有回复（包括嵌套回复）
        """
        comment = self.get_object()
        replies = comment.replies.filter(is_deleted=False)
        serializer = CommentReplySerializer(replies, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def reply(self, request, pk=None):
        """
        回复评论或其他回复
        """
        comment = self.get_object()
        serializer = CommentReplySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            user=request.user,
            comment=comment
        )
        # 更新评论的回复数
        comment.reply_count += 1
        comment.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def delete_comment(self, request, pk=None):
        """
        管理员删除评论
        """
        comment = self.get_object()
        if request.user.role != 'admin':
            return Response({'detail': '只有管理员可以删除评论'}, status=status.HTTP_403_FORBIDDEN)

        deleted_reason = request.data.get('deleted_reason', '违规评论')
        comment.is_deleted = True
        comment.deleted_reason = deleted_reason
        comment.save()

        # 发送通知
        Notification.objects.create(
            user=comment.user,
            type='comment_deleted',
            content=f'您的评论被管理员删除，原因：{deleted_reason}'
        )

        return Response({'status': 'comment deleted'})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def delete_reply(self, request, pk=None):
        """
        管理员删除回复
        """
        comment = self.get_object()
        if request.user.role != 'admin':
            return Response({'detail': '只有管理员可以删除回复'}, status=status.HTTP_403_FORBIDDEN)

        reply_id = request.data.get('reply_id')
        deleted_reason = request.data.get('deleted_reason', '违规回复')
        
        try:
            reply = CommentReply.objects.get(id=reply_id, comment=comment)
            reply.is_deleted = True
            reply.deleted_reason = deleted_reason
            reply.save()
            
            # 更新评论的回复数
            comment.reply_count = max(0, comment.reply_count - 1)
            comment.save()
            
            # 发送通知
            Notification.objects.create(
                user=reply.user,
                type='comment_deleted',
                content=f'您的回复被管理员删除，原因：{deleted_reason}'
            )
            
            return Response({'status': 'reply deleted'})
        except CommentReply.DoesNotExist:
            return Response({'detail': '回复不存在'}, status=status.HTTP_404_NOT_FOUND)


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    消息通知视图集
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        获取当前用户的通知
        """
        return Notification.objects.filter(user=self.request.user).order_by('-create_time')

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def mark_as_read(self, request, pk=None):
        """
        标记通知为已读
        """
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'marked as read'})

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def mark_all_as_read(self, request):
        """
        标记所有通知为已读
        """
        notifications = self.get_queryset().filter(is_read=False)
        notifications.update(is_read=True)
        return Response({'status': 'all notifications marked as read'})

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def unread_count(self, request):
        """
        获取未读通知数量
        """
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'unread_count': count})


class ResourceCommentViewSet(viewsets.ModelViewSet):
    """
    学习资源评论视图集
    """
    serializer_class = ResourceCommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        获取指定资源的评论
        """
        resource_id = self.kwargs.get('resource_pk')
        return ResourceComment.objects.filter(
            resource_id=resource_id,
            is_deleted=False
        ).order_by('-create_time')

    def create(self, request, resource_pk=None, *args, **kwargs):
        """
        创建资源评论
        """
        serializer = ResourceCommentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            user=request.user,
            resource_id=resource_pk
        )
        return Response(ResourceCommentSerializer(serializer.instance, context={'request': request}).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None, resource_pk=None):
        """
        点赞/取消点赞资源评论
        """
        resource_comment = self.get_object()
        user = request.user
        
        # 查找是否已点赞
        like, created = ResourceCommentLike.objects.get_or_create(
            user=user,
            resource_comment=resource_comment
        )

        if created:
            # 新增点赞
            resource_comment.like_count += 1
            resource_comment.save()
            return Response({'status': 'liked', 'like_count': resource_comment.like_count})
        else:
            # 取消点赞
            like.delete()
            resource_comment.like_count = max(0, resource_comment.like_count - 1)
            resource_comment.save()
            return Response({'status': 'unliked', 'like_count': resource_comment.like_count})


class AdminUserManagementViewSet(viewsets.ViewSet):
    """
    管理员用户管理视图集
    """
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def ban_user(self, request, pk=None):
        """
        禁言用户
        """
        if request.user.role != 'admin':
            return Response({'detail': '只有管理员可以禁言用户'}, status=status.HTTP_403_FORBIDDEN)

        try:
            user = SysUser.objects.get(pk=pk)
        except SysUser.DoesNotExist:
            return Response({'detail': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)

        ban_reason = request.data.get('ban_reason', '违规行为')
        # 这里简化处理，实际项目中可能需要更复杂的禁言逻辑
        user.status = 1  # 0: 正常, 1: 禁用
        user.save()

        # 发送通知
        Notification.objects.create(
            user=user,
            type='user_banned',
            content=f'您被管理员禁言，原因：{ban_reason}'
        )

        return Response({'status': 'user banned'})
