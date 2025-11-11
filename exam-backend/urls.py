from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/user/', include('user.urls')),       # 用户相关接口
    path('api/exam/', include('exam.urls')),       # 考试相关接口
    path('api/question/', include('question.urls')), # 题目相关接口
]