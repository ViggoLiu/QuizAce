from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import os
from django.utils.text import slugify
from user.models import SysUser, StudentProfile, TeacherProfile
from user.serializers import UserSerializer, AdminUserManageSerializer
from learning_resource.models import LearningResource
from forum.models import ForumComment, CommentReply, ResourceComment


class LoginView(View):

    def get(self, request):
        username = request.GET.get('username')
        password = request.GET.get('password')
        print(f'登录请求（GET）：username={username}, password={password}')
        return self._login(username, password)

    def post(self, request):
        # 尝试从JSON请求体获取数据
        import json
        username = None
        password = None
        
        try:
            # 尝试解析JSON数据
            body = request.body.decode('utf-8')
            data = json.loads(body)
            username = data.get('username')
            password = data.get('password')
            print(f'从JSON获取：username={username}, password={password}')
        except:
            # 如果JSON解析失败，尝试从表单数据获取
            username = request.POST.get('username')
            password = request.POST.get('password')
            print(f'从表单获取：username={username}, password={password}')
        
        # 最后尝试从URL参数获取
        if not username:
            username = request.GET.get('username')
        if not password:
            password = request.GET.get('password')
        
        print(f'登录请求（POST）：username={username}, password={password}')
        return self._login(username, password)

    def _login(self, username, password):
        try:
            user = SysUser.objects.get(username=username)
            print(f'找到用户：{user.username}，密码哈希：{user.password}')
            # 验证密码（使用AbstractBaseUser内置的check_password方法）
            if user.check_password(password):
                print('密码验证成功')
                # 使用新的djangorestframework-simplejwt生成token
                refresh = RefreshToken.for_user(user)
                token = str(refresh.access_token)
            else:
                print('密码验证失败')
                return JsonResponse({'code': 500, 'info': '用户名或者密码错误'})
        except SysUser.DoesNotExist:
            print(f'用户不存在：{username}')
            return JsonResponse({'code': 500, 'info': '用户名或者密码错误'})
        except Exception as e:
            print(f'登录异常：{e}')
            return JsonResponse({'code': 500, 'info': '用户名或者密码错误'})
        return JsonResponse({'code': 200, 'token': token, 'user': UserSerializer(user).data, 'info': '登录成功'})

    # Create your views here.


class TestView(View):

    def get(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')
        if token != None and token != "":
            userList_obj = SysUser.objects.all()
            print(userList_obj, type(userList_obj))
            userList_dict = userList_obj.values()
            print(userList_dict, type(userList_dict))
            userList = list(userList_dict)
            print(userList, type(userList))
            return JsonResponse({'code': 200, 'info': '测试!', 'data': userList})
        else:
            return JsonResponse({'code': 401, 'info': '没有访问权限！'})


class JwtTestView(View):

    def get(self, request):
        user = SysUser.objects.get(username='python222', password='123456')
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        return JsonResponse({'code': 200, 'access_token': access_token, 'refresh_token': refresh_token})


class RegisterView(View):

    def post(self, request):
        username = request.GET.get('username')
        password = request.GET.get('password')
        email=request.GET.get('email')
        
        # 检查用户名是否已存在
        if SysUser.objects.filter(username=username).exists():
            return JsonResponse({'code': 400, 'info': '用户名已存在'})
        
        try:
            # 创建用户，角色默认为student，密码自动哈希
            user = SysUser.objects.create_user(
                username=username,
                password=password,
                email=email,
                role='student'  # 默认角色为学生
            )
            
            # 为学生用户创建对应的学生信息记录
            StudentProfile.objects.create(user=user)
            
            # 生成JWT token
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            
            return JsonResponse({'code': 200, 'info': '注册成功', 'user': UserSerializer(user).data, 'access_token': access_token, 'refresh_token': refresh_token})
        except Exception as e:
            print(e)
            return JsonResponse({'code': 500, 'info': '注册失败'})


class UserInfoView(APIView):
    """获取当前用户信息"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response({'code': 200, 'data': serializer.data, 'info': '获取用户信息成功'})


class AvatarUploadView(APIView):
    """上传头像"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        if 'avatar' not in request.FILES:
            return Response({'code': 400, 'info': '没有上传文件'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        avatar = request.FILES['avatar']
        
        # 确保头像目录存在
        avatar_dir = os.path.join(settings.MEDIA_ROOT, 'avatars')
        if not os.path.exists(avatar_dir):
            os.makedirs(avatar_dir)
        
        # 获取原始文件名和扩展名
        original_filename = avatar.name
        # 分离文件名和扩展名，ext包含点号（如：.jpg）
        filename_without_ext, ext = os.path.splitext(original_filename)
        
        # 仅对文件名部分使用slugify，保留扩展名
        slugified_filename = slugify(filename_without_ext)
        
        # 生成唯一文件名，保留原始扩展名
        filename = f"{user.id}_{slugified_filename}{ext}"
        filepath = os.path.join(avatar_dir, filename)
        
        # 保存文件
        with open(filepath, 'wb+') as destination:
            for chunk in avatar.chunks():
                destination.write(chunk)
        
        # 更新用户头像URL
        user.avatar = f"/media/avatars/{filename}"
        user.save()
        
        # 修复：返回格式，确保前端能正确获取avatar URL
        return Response({'code': 200, 'data': {'avatar': user.avatar}, 'info': '头像上传成功'})

class UserUpdateView(APIView):
    """更新用户信息"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request, user_id):
        # 验证用户是否有权限更新自身信息
        if str(request.user.id) != user_id:
            return Response({'code': 403, 'info': '没有权限更新该用户信息'}, status=status.HTTP_403_FORBIDDEN)
        
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({'code': 200, 'data': serializer.data, 'info': '更新用户信息成功'})
        
        return Response({'code': 400, 'info': '更新失败', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class AdminUserListCreateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def _ensure_admin(self, request):
        if getattr(request.user, 'role', None) != 'admin':
            return Response({'code': 403, 'info': '仅管理员可执行此操作'}, status=status.HTTP_403_FORBIDDEN)

    def get(self, request):
        denied = self._ensure_admin(request)
        if denied:
            return denied

        role = request.GET.get('role')
        keyword = request.GET.get('keyword', '')

        manageable_roles = ['student', 'teacher', 'admin']
        qs = SysUser.objects.filter(role__in=manageable_roles)
        if role in manageable_roles:
            qs = qs.filter(role=role)
        if keyword:
            qs = qs.filter(username__icontains=keyword)

        serializer = AdminUserManageSerializer(qs.order_by('-create_time'), many=True)
        return Response({'code': 200, 'info': '获取用户列表成功', 'data': serializer.data})

    def post(self, request):
        denied = self._ensure_admin(request)
        if denied:
            return denied

        serializer = AdminUserManageSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({'code': 200, 'info': '创建用户成功', 'data': serializer.data})
        return Response({'code': 400, 'info': '创建用户失败', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class AdminUserDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def _ensure_admin(self, request):
        if getattr(request.user, 'role', None) != 'admin':
            return Response({'code': 403, 'info': '仅管理员可执行此操作'}, status=status.HTTP_403_FORBIDDEN)

    def _get_user(self, pk):
        manageable_roles = ['student', 'teacher', 'admin']
        try:
            return SysUser.objects.get(id=pk, role__in=manageable_roles)
        except SysUser.DoesNotExist:
            return None

    def put(self, request, pk):
        denied = self._ensure_admin(request)
        if denied:
            return denied

        user = self._get_user(pk)
        if not user:
            return Response({'code': 404, 'info': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)

        serializer = AdminUserManageSerializer(user, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({'code': 200, 'info': '更新用户成功', 'data': serializer.data})
        return Response({'code': 400, 'info': '更新用户失败', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        denied = self._ensure_admin(request)
        if denied:
            return denied

        user = self._get_user(pk)
        if not user:
            return Response({'code': 404, 'info': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)

        user.delete()
        return Response({'code': 200, 'info': '删除用户成功', 'data': None})


class AdminOverviewStatsView(APIView):
    """管理员看板数据"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if getattr(request.user, 'role', None) != 'admin':
            return Response({'code': 403, 'info': '仅管理员可执行此操作'}, status=status.HTTP_403_FORBIDDEN)

        student_count = SysUser.objects.filter(role='student').count()
        teacher_count = SysUser.objects.filter(role='teacher').count()
        admin_count = SysUser.objects.filter(role='admin').count()

        pending_resource_count = LearningResource.objects.filter(status=0).count()
        approved_resource_count = LearningResource.objects.filter(status=1).count()
        rejected_resource_count = LearningResource.objects.filter(status=2).count()
        total_resource_count = pending_resource_count + approved_resource_count + rejected_resource_count

        forum_forum_count = ForumComment.objects.filter(is_deleted=False).count()
        forum_reply_count = CommentReply.objects.filter(is_deleted=False).count()
        resource_comment_count = ResourceComment.objects.filter(is_deleted=False).count()
        forum_comment_count = forum_forum_count + forum_reply_count + resource_comment_count

        data = {
            'student_count': student_count,
            'teacher_count': teacher_count,
            'admin_count': admin_count,
            'total_user_count': student_count + teacher_count + admin_count,
            'pending_resource_count': pending_resource_count,
            'approved_resource_count': approved_resource_count,
            'rejected_resource_count': rejected_resource_count,
            'total_resource_count': total_resource_count,
            'forum_comment_count': forum_comment_count,
            'forum_forum_comment_count': forum_forum_count,
            'forum_reply_count': forum_reply_count,
            'resource_comment_count': resource_comment_count,
        }

        return Response({'code': 200, 'info': '获取运营数据成功', 'data': data})
