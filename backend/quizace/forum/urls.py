from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
     ForumCommentViewSet,
     NotificationViewSet,
     ResourceCommentViewSet,
     AdminUserManagementViewSet,
     AdminForumModerationViewSet
)


# 创建路由
router = DefaultRouter()

# 注册论坛评论路由
router.register(r'forum/comments', ForumCommentViewSet, basename='forum-comment')

# 注册消息通知路由
router.register(r'notifications', NotificationViewSet, basename='notification')

# 注册管理员用户管理路由
router.register(r'admin/users', AdminUserManagementViewSet, basename='admin-user')

# 注册论坛管理路由
router.register(r'admin/moderation', AdminForumModerationViewSet, basename='admin-forum-moderation')

# 定义资源评论路由，使用嵌套路由
urlpatterns = [
    path('', include(router.urls)),
    path('resources/<int:resource_pk>/comments/', 
         ResourceCommentViewSet.as_view({'get': 'list', 'post': 'create'}), 
         name='resource-comments'),
    path('resources/<int:resource_pk>/comments/<int:pk>/', 
         ResourceCommentViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), 
         name='resource-comment-detail'),
    path('resources/<int:resource_pk>/comments/<int:pk>/like/', 
         ResourceCommentViewSet.as_view({'post': 'like'}), 
         name='resource-comment-like'),
]
