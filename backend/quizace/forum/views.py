from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime, timedelta
from .models import ForumComment, CommentLike, CommentReply, Notification, ResourceComment, ResourceCommentLike
from .serializers import (
    ForumCommentSerializer,
    CommentLikeSerializer,
    CommentReplySerializer,
    NotificationSerializer,
    ResourceCommentSerializer,
    ResourceCommentCreateSerializer,
    AdminForumSpeechSerializer
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


class AdminForumSpeechPagination(PageNumberPagination):
    """论坛发言分页配置"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class AdminForumModerationViewSet(viewsets.ViewSet):
    """管理员论坛发言管理视图集"""
    permission_classes = [IsAuthenticated]
    pagination_class = AdminForumSpeechPagination

    def _parse_date(self, value, is_end=False):
        if not value:
            return None
        try:
            parsed = datetime.strptime(value, '%Y-%m-%d')
            if is_end:
                parsed += timedelta(days=1)
            return timezone.make_aware(parsed, timezone.get_current_timezone())
        except ValueError:
            return None

    def list(self, request):
        if request.user.role != 'admin':
            return Response({'detail': '只有管理员可以执行该操作'}, status=status.HTTP_403_FORBIDDEN)

        keyword = request.query_params.get('keyword')
        role = request.query_params.get('role')
        speech_type = request.query_params.get('type')
        source_type = request.query_params.get('source')
        start_date = self._parse_date(request.query_params.get('start_date'))
        end_date = self._parse_date(request.query_params.get('end_date'), is_end=True)

        comment_qs = ForumComment.objects.filter(is_deleted=False)
        reply_qs = CommentReply.objects.filter(is_deleted=False)
        resource_comment_qs = ResourceComment.objects.filter(is_deleted=False)

        if keyword:
            comment_qs = comment_qs.filter(content__icontains=keyword)
            reply_qs = reply_qs.filter(content__icontains=keyword)
            resource_comment_qs = resource_comment_qs.filter(content__icontains=keyword)
        if role:
            comment_qs = comment_qs.filter(user__role=role)
            reply_qs = reply_qs.filter(user__role=role)
            resource_comment_qs = resource_comment_qs.filter(user__role=role)
        if start_date:
            comment_qs = comment_qs.filter(create_time__gte=start_date)
            reply_qs = reply_qs.filter(create_time__gte=start_date)
            resource_comment_qs = resource_comment_qs.filter(create_time__gte=start_date)
        if end_date:
            comment_qs = comment_qs.filter(create_time__lt=end_date)
            reply_qs = reply_qs.filter(create_time__lt=end_date)
            resource_comment_qs = resource_comment_qs.filter(create_time__lt=end_date)

        records = []
        include_comments = speech_type in (None, '', 'comment')
        include_replies = speech_type in (None, '', 'reply')
        include_resource_comments = speech_type in (None, '', 'resource_comment')

        source_allows_forum = source_type in (None, '', 'forum')
        source_allows_resource = source_type in (None, '', 'resource')

        if include_comments and source_allows_forum:
            for comment in comment_qs.select_related('user'):
                records.append({
                    'id': comment.id,
                    'type': 'comment',
                    'origin': 'forum',
                    'content': comment.content,
                    'user': comment.user,
                    'to_user': None,
                    'comment_id': comment.id,
                    'parent_reply_id': None,
                    'like_count': comment.like_count,
                    'reply_count': comment.reply_count,
                    'create_time': comment.create_time,
                    'target_excerpt': None,
                    'resource': None,
                    'rating': None
                })

        if include_replies and source_allows_forum:
            for reply in reply_qs.select_related('user', 'to_user', 'comment', 'parent_reply'):
                records.append({
                    'id': reply.id,
                    'type': 'reply',
                    'origin': 'forum',
                    'content': reply.content,
                    'user': reply.user,
                    'to_user': reply.to_user,
                    'comment_id': reply.comment_id,
                    'parent_reply_id': reply.parent_reply_id,
                    'like_count': None,
                    'reply_count': None,
                    'create_time': reply.create_time,
                    'target_excerpt': reply.comment.content[:60] if reply.comment else None,
                    'resource': None,
                    'rating': None
                })

        if include_resource_comments and source_allows_resource:
            for res_comment in resource_comment_qs.select_related('user', 'resource'):
                resource_context = None
                if res_comment.resource:
                    resource_context = {
                        'id': res_comment.resource_id,
                        'name': res_comment.resource.name,
                        'course': res_comment.resource.course,
                    }
                records.append({
                    'id': res_comment.id,
                    'type': 'resource_comment',
                    'origin': 'resource',
                    'content': res_comment.content,
                    'user': res_comment.user,
                    'to_user': None,
                    'comment_id': None,
                    'parent_reply_id': None,
                    'like_count': res_comment.like_count,
                    'reply_count': None,
                    'create_time': res_comment.create_time,
                    'target_excerpt': res_comment.resource.description[:60] if res_comment.resource and res_comment.resource.description else None,
                    'resource': resource_context,
                    'rating': res_comment.rating,
                })

        records.sort(key=lambda item: item['create_time'], reverse=True)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(records, request)
        serializer = AdminForumSpeechSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def destroy(self, request, pk=None):
        if request.user.role != 'admin':
            return Response({'detail': '只有管理员可以执行该操作'}, status=status.HTTP_403_FORBIDDEN)

        speech_type = request.query_params.get('type', 'comment')
        deleted_reason = request.data.get('deleted_reason') or '违规发言'

        if speech_type == 'resource_comment':
            resource_comment = get_object_or_404(ResourceComment, pk=pk, is_deleted=False)
            resource_comment.is_deleted = True
            resource_comment.save()

            Notification.objects.create(
                user=resource_comment.user,
                type='comment_deleted',
                content=f'您的资源评论被管理员删除，原因：{deleted_reason}'
            )
            return Response({'status': 'resource comment deleted'})

        if speech_type == 'reply':
            reply = get_object_or_404(CommentReply, pk=pk, is_deleted=False)
            reply.is_deleted = True
            reply.deleted_reason = deleted_reason
            reply.save()

            comment = reply.comment
            if comment:
                comment.reply_count = max(0, comment.reply_count - 1)
                comment.save()

            Notification.objects.create(
                user=reply.user,
                type='comment_deleted',
                content=f'您的回复被管理员删除，原因：{deleted_reason}'
            )
            return Response({'status': 'reply deleted'})

        comment = get_object_or_404(ForumComment, pk=pk, is_deleted=False)
        comment.is_deleted = True
        comment.deleted_reason = deleted_reason
        comment.save()

        Notification.objects.create(
            user=comment.user,
            type='comment_deleted',
            content=f'您的评论被管理员删除，原因：{deleted_reason}'
        )
        return Response({'status': 'comment deleted'})
