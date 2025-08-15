from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, ListModelMixin
from rest_framework.request import Request
from rest_framework.generics import GenericAPIView
from .serializers import RegisterSerializer, LoginSerializer, TreeMenuSerializer, UserDetailSerializer
from authSystem.controller.auth_controller import AuthController
from core.exceptions import APIError
from authSystem.services.sms import SmsService
from utils.rules import phone_validator
from .models import MenuModel, RoleMenuModel, UserModel
from django.shortcuts import get_object_or_404


# Create your views here.
class RegisterView(APIView):
    def post(self, request: Request, *args, **kwargs):
        """
        入参： {
            "username": str,
            "password": str,
            "confirmPassword": str
        }
        """
        request_data = request.data
        # TODO: 注册逻辑
        serializer = RegisterSerializer(data=request_data)
        # 校验
        if not serializer.is_valid():
            return JsonResponse({
                'code': 400,
                'message': '注册失败',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        # 保存数据
        serializer.save()
        # TODO: 返回结果
        return JsonResponse({'code': 200, 'message': '注册成功'})


class SendCode(APIView):
    def get(self, request, phone: str):
        """发送验证码"""
        if not phone_validator(phone):
            return JsonResponse({
                'code': 400,
                'message': '手机号格式不正确！'
            })
        SmsService().send_sms_code(phone)
        return JsonResponse({
            'code': 200,
            'message': 'success!'
        })


class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        """登陆"""
        try:
            # 序列化数据
            serializer = LoginSerializer(data=request.data)
            if not serializer.is_valid():
                return JsonResponse({
                    'code': 400,
                    'message': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            # 处理登陆
            controller = AuthController()
            result = controller.login(serializer.validated_data)
            result['avatar'] = request.build_absolute_uri(result.get('avatar'))
            # 序列化user
            # 返回结果
            response = JsonResponse({
                'code': 200,
                'data': result
            })

            # 设置安全Cookie
            # set_auth_cookie(
            #     response=response,
            #     token=result.get('token'),
            #     remember_me=serializer.validated_data.get('remember_me', False)
            # )
            return response

        except APIError as e:
            return JsonResponse({
                'code': e.code,
                'message': e.message
            }, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    def post(self, request, *args, **kwargs):
        return JsonResponse({'code': 200, 'message': '登出成功'})


class MenuView(APIView):
    def get(self, request):
        try:
            # 直接从request中获取中间件解析的role_id
            role_id = request.role_id
            role_menus = RoleMenuModel.objects.filter(role=role_id)
            menu_ids = [rm.menu.id for rm in role_menus]

            menus = MenuModel.objects.filter(
                id__in=menu_ids,
                parent__isnull=True,
                visible=True
            ).order_by('order')

            serializer = TreeMenuSerializer(menus, many=True)
            return JsonResponse({
                'code': 200,
                'message': '成功获取菜单',
                'data': serializer.data
            })

        except Exception as e:
            return JsonResponse({
                'code': 500,
                'message': '获取菜单失败',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MineView(GenericAPIView, RetrieveModelMixin):
    """个人中心视图"""
    serializer_class = UserDetailSerializer

    def get(self, request, *args, **kwargs):
        """获取个人中心信息"""
        user = get_object_or_404(UserModel, id=request.user_id)
        if not user:
            return JsonResponse({
                'code': 400,
                'message': '获取用户信息失败!',
            }, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(user)
        return JsonResponse({
            'code': 200,
            'message': 'success',
            'data': serializer.data
        })

    def get_serializer_context(self):
        """添加request到serializer context"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
