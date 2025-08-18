from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse, HttpRequest
from django.core.cache import cache
from rest_framework import status
from utils.token import verify_token

WHITE_LIST = ['/auth/login', '/auth/register', '/auth/send_code', '/auth/refresh', '/media', '/swagger', '/redoc']


class TokenAuthMiddleware(MiddlewareMixin):
    """token认证中间件"""

    def process_request(self, request: HttpRequest):
        for i in WHITE_LIST:
            if request.path.find(i) != -1:
                return None

        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return JsonResponse({
                'code': 401,
                'message': '未提供认证Token'
            }, status=status.HTTP_401_UNAUTHORIZED)
        payload = verify_token(auth_header)
        if not payload:
            return JsonResponse({
                'code': 401,
                'message': 'Token无效或已过期'
            }, status=status.HTTP_401_UNAUTHORIZED)

        user_id = payload.get('user_id')
        if not cache.get(f'refresh_token:{user_id}'):
            return JsonResponse({
                'code': 401,
                'message': '请先登陆'
            })

        # 将用户信息和角色信息存入request
        request.user_id = payload.get('user_id')
        request.role_id = payload.get('role_id')
        request.payload = payload
        return None
