from django.urls import path

from user.views import (
    TestView,
    JwtTestView,
    LoginView,
    RegisterView,
    UserInfoView,
    AvatarUploadView,
    UserUpdateView,
    AdminUserListCreateView,
    AdminUserDetailView,
    AdminOverviewStatsView,
)

urlpatterns = [
    path('test', TestView.as_view(), name='test'),  # 测试
    path('test/', TestView.as_view()),
    path('jwt_test', JwtTestView.as_view(), name='jwt_test'),  # jwt测试
    path('jwt_test/', JwtTestView.as_view()),
    path('login', LoginView.as_view(), name='login'),  # 登录
    path('login/', LoginView.as_view()),
    path('register', RegisterView.as_view(), name='register'),  # 注册
    path('register/', RegisterView.as_view()),
    path('info/', UserInfoView.as_view(), name='user_info'),  # 获取当前用户信息
    path('upload/avatar/', AvatarUploadView.as_view(), name='avatar_upload'),  # 上传头像
    path('update/<str:user_id>/', UserUpdateView.as_view(), name='user_update'),  # 更新用户信息
    path('admin/users/', AdminUserListCreateView.as_view(), name='admin_user_list_create'),
    path('admin/users/<int:pk>/', AdminUserDetailView.as_view(), name='admin_user_detail'),
    path('admin/overview/', AdminOverviewStatsView.as_view(), name='admin_overview'),
]
