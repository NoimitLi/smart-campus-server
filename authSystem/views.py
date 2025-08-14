from django.http import JsonResponse
from django.views.generic import View
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from .serializers import RegisterSerializer


# Create your views here.
class RegisterView(APIView):
    def post(self, request: Request, *args, **kwargs):
        """
        入参： {
            "username": str,
            "password": str,
            "confirmPassword": str
        }
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        request_data = request.data
        # print(request_data)
        # TODO: 注册逻辑
        serializer = RegisterSerializer(data=request_data)
        # 校验
        if not serializer.is_valid():
            return JsonResponse({
                'code': 400,
                'msg': '注册失败',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        # 保存数据
        serializer.save()
        # TODO: 返回结果
        return JsonResponse({'code': 200, 'msg': '注册成功'})


class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        return JsonResponse({'code': 200, 'msg': '登录成功'})


class LogoutView(APIView):
    def post(self, request, *args, **kwargs):
        return JsonResponse({'code': 200, 'msg': '登出成功'})


class MineView(APIView):
    def get(self, request, user_id, *args, **kwargs):
        print(user_id)
        return JsonResponse({'code': 200, 'msg': '个人中心'})
