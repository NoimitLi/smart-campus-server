from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.request import Request
from rest_framework.generics import GenericAPIView
from .serializers import RegisterSerializer, LoginSerializer, TreeMenuSerializer, UserDetailSerializer
from apps.oauth.controller.auth_controller import AuthController
from apps.oauth.services.sms import SmsService
from core.exceptions import APIError, AuthFailed
from utils.rules import phone_validator
from Base.Response import APIResponse
from .models import MenuModel, RoleMenuModel, UserModel


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
            return APIResponse(
                data=serializer.errors,
                message='注册失败',
                status=status.HTTP_400_BAD_REQUEST
            )
        # 保存数据
        serializer.save()
        # TODO: 返回结果
        return APIResponse(message='注册成功')


class SendCode(APIView):
    def get(self, request, phone: str):
        """发送验证码"""
        if not phone_validator(phone):
            return APIResponse(message='手机号格式不正确！', status=status.HTTP_400_BAD_REQUEST)
        SmsService().send_sms_code(phone)
        return APIResponse()


class LoginView(APIView):
    """登录接口 - 优化版"""

    def post(self, request, *args, **kwargs):
        try:
            serializer = LoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            controller = AuthController()
            result = controller.login(serializer.validated_data)

            # 处理头像URL
            if result['user'].get('avatar'):
                result['user']['avatar'] = request.build_absolute_uri(result['user']['avatar'])

            # 设置HttpOnly Cookie存储refresh_token
            response = APIResponse({
                'user': result['user'],
                'access_token': result['access_token']
            }, status=status.HTTP_200_OK)

            response.set_cookie(
                key='refresh_token',
                value=result['refresh_token'],
                max_age=int(AuthController.REFRESH_TOKEN_EXPIRE.total_seconds()),
                httponly=True,
                secure=request.is_secure(),  # 生产环境应为True
                samesite='Lax',
                path='/api/auth/refresh'  # 限制Cookie只发送到刷新接口
            )

            return response

        except APIError as e:
            return APIResponse(code=e.code, message=e.message, status=status.HTTP_400_BAD_REQUEST)


class TokenRefreshView(APIView):
    """Token刷新接口"""

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.COOKIES.get('refresh_token')
            print(request.COOKIES)
            if not refresh_token:
                raise AuthFailed('缺少Refresh Token')

            controller = AuthController()
            result = controller.refresh_token(refresh_token)

            response = APIResponse({
                'access_token': result['access_token']
            })

            # 返回新的access_token
            return response

        except APIError as e:
            return APIResponse(code=e.code, message=e.message, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    """登出接口"""

    def post(self, request, *args, **kwargs):
        try:
            payload = request.payload
            if payload.get('token_type') != 'access':
                raise AuthFailed('无效的Token类型')

            # 执行登出逻辑
            controller = AuthController()
            controller.logout(payload['user_id'])

            # 清除Cookie
            response = APIResponse(message='登出成功')
            response.delete_cookie('refresh_token')
            return response

        except APIError as e:
            return APIResponse(code=e.code, message=e.message, status=status.HTTP_400_BAD_REQUEST)


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
            return APIResponse(data=serializer.data, message='成功获取菜单')

        except APIError as e:
            return APIResponse(code=e.code, message='获取菜单失败', status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MineView(GenericAPIView, RetrieveModelMixin):
    """个人中心视图"""
    serializer_class = UserDetailSerializer

    def get(self, request, *args, **kwargs):
        """获取个人中心信息"""
        user = get_object_or_404(UserModel, id=request.user_id)
        if not user:
            return APIResponse(message='获取用户信息失败!', status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(user)
        return APIResponse(data=serializer.data)

    def get_serializer_context(self):
        """添加request到serializer context"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
