"""
URL configuration for quizace project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from django.urls import include
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path('user/',include('user.urls')),
    path('learning_resource/',include('learning_resource.urls')),
    path('exam/', include('exam.urls')),
    path('forum/', include('forum.urls')),
]

# 在开发环境中提供媒体文件的服务
if settings.DEBUG:
    # 使用自定义的媒体文件服务视图来替代默认的static服务
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', views.custom_serve_media, {'document_root': settings.MEDIA_ROOT})
    ]
