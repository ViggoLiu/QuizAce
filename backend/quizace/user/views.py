from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from rest_framework_simplejwt.tokens import RefreshToken

from user.models import SysUser, SysUserSerializer


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
        return JsonResponse({'code': 200, 'token': token, 'user': SysUserSerializer(user).data, 'info': '登录成功'})

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
            from user.models import StudentProfile
            StudentProfile.objects.create(user=user)
            
            # 生成JWT token
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            
            return JsonResponse({'code': 200, 'info': '注册成功', 'user': SysUserSerializer(user).data, 'access_token': access_token, 'refresh_token': refresh_token})
        except Exception as e:
            print(e)
            return JsonResponse({'code': 500, 'info': '注册失败'})
