from django.http import HttpResponse, JsonResponse, FileResponse
from django.shortcuts import render
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import os
import mimetypes
from django.conf import settings


def runoob(request):
    context          = {}
    context['hello'] = 'Hello World!'
    return render(request, 'runoob.html', context)


def custom_exception_handler(exc, context):
    """
    自定义异常处理程序，确保所有的认证错误都返回一致的JSON格式
    """
    # 首先使用DRF的默认异常处理程序获取响应
    response = exception_handler(exc, context)
    
    # 如果响应是None，说明异常没有被DRF的默认处理程序处理
    if response is None:
        return response
    
    # 检查是否是认证相关的错误
    if hasattr(exc, 'status_code') and exc.status_code == status.HTTP_401_UNAUTHORIZED:
        # 返回一致的JSON格式
        return Response({
            'code': 401,
            'info': '认证失败：' + getattr(response, 'detail', 'Authentication credentials were not provided.'),
            'data': None
        }, status=status.HTTP_200_OK)
    
    # 对于其他错误，返回原始响应
    return response


def custom_serve_media(request, path, document_root=None):
    """
    自定义媒体文件服务视图，确保正确设置文件编码
    """
    if document_root is None:
        document_root = settings.MEDIA_ROOT
    
    # 构建文件的完整路径
    file_path = os.path.join(document_root, path)
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        return JsonResponse({
            'code': 404,
            'info': '文件不存在',
            'data': None
        })
    
    # 确定文件的MIME类型
    mime_type, encoding = mimetypes.guess_type(file_path)
    mime_type = mime_type or 'application/octet-stream'
    
    # 对于文本文件，添加charset参数
    if mime_type.startswith('text/'):
        mime_type = f'{mime_type}; charset=utf-8'
    
    # 提供文件下载/查看
    response = FileResponse(open(file_path, 'rb'), content_type=mime_type)
    
    # 设置Content-Disposition为inline，让浏览器尝试预览文件
    filename = os.path.basename(file_path)
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    
    return response