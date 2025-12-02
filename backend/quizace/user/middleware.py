from django.http import HttpResponse, JsonResponse
from django.utils.deprecation import MiddlewareMixin
from jwt import ExpiredSignatureError, InvalidTokenError, PyJWTError
from rest_framework_simplejwt.backends import TokenBackend
from rest_framework_simplejwt.exceptions import TokenBackendExpiredToken, TokenBackendError, InvalidToken

from user.models import SysUser


class JwtAuthenticationMiddleware(MiddlewareMixin):

    def process_request(self, request):
        white_list = ["/user/login", "/user/register"]  # 请求白名单
        path = request.path
        if path not in white_list and not path.startswith("/media"):
            print("要进行token验证")
            token = request.META.get('HTTP_AUTHORIZATION')
            print("token:", token)
            
            # 处理Bearer前缀
            if token and token.startswith('Bearer '):
                token = token[7:]  # 去除Bearer前缀
            
            try:
                # 使用新的djangorestframework-simplejwt验证和解码token
                from django.conf import settings
                from rest_framework_simplejwt.tokens import AccessToken
                
                # 验证token并获取payload
                access_token = AccessToken(token)
                payload = access_token.payload
                
                # 将用户信息存储到request对象中
                user_id = payload.get('user_id')
                user = SysUser.objects.get(id=user_id)
                request.user = user
                request.auth = access_token  # 设置request.auth以兼容DRF的认证机制
                
            except (ExpiredSignatureError, TokenBackendExpiredToken):
                return JsonResponse({'code': 401, 'info': 'Token过期，请重新登录！', 'data': None})
            except (InvalidTokenError, InvalidToken, TokenBackendError):
                return JsonResponse({'code': 401, 'info': 'Token验证失败！', 'data': None})
            except PyJWTError:
                return JsonResponse({'code': 401, 'info': 'Token验证异常！', 'data': None})
            except SysUser.DoesNotExist:
                return JsonResponse({'code': 401, 'info': '用户不存在！', 'data': None})
        else:
            print("不需要token验证")
        
        # 不要返回None，否则会中断请求处理
        return None
