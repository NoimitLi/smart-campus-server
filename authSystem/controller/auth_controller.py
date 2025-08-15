from core.exceptions import AuthFailed
from django.contrib.auth import authenticate
from django.utils import timezone
from authSystem.services.sms import SmsService
from ..models import UserRoleModel, RolePermissionModel


class AuthController:
    """认证业务控制器"""

    def __init__(self):
        pass

    def login(self, data: dict):
        """统一登录处理"""
        # 分发登录方式
        if 'username' in data:
            return self._account_login(data['username'], data['password'])
        else:
            return self._phone_login(data['phone'], data['code'])

    def _account_login(self, username: str, password: str):
        """账号密码登录"""
        user = authenticate(username=username, password=password, mode='account')
        if not user:
            raise AuthFailed('账号或密码错误')
        return self._generate_token(user)

    def _phone_login(self, phone: str, code: str):
        """手机号登录"""
        if not SmsService().verify_sms_code(phone, code):
            raise AuthFailed('验证码错误')

        user = authenticate(phone=phone, code=code, mode='phone')
        if not user:
            raise AuthFailed('手机号未注册')

        return self._generate_token(user)

    def _generate_token(self, user):
        """生成访问令牌"""
        from utils.token import generate_token
        # 获取用户角色
        try:
            user_role = UserRoleModel.objects.get(user=user.id)
            role = user_role.role
        except UserRoleModel.DoesNotExist:
            role = None
        # 获取角色权限
        permissions = []
        if role:
            # 获取通过角色直接关联的权限
            role_permissions = RolePermissionModel.objects.filter(role=role.id)
            permissions = [rp.permission.code for rp in role_permissions]

            # 获取通过菜单关联的权限（如果需要）
            # role_menus = RoleMenuModel.objects.filter(role_id=role.id)
            # 可以添加菜单权限的处理逻辑
        # 更新最后登录时间
        user.last_login_time = timezone.now()
        user.save(update_fields=['last_login_time'])
        # 生成令牌
        token = generate_token({
            'user_id': user.id,
            'username': user.username,
            'role_id': role.id if role else '',
            # 'permissions': permissions
            'last_login_time': user.last_login_time.strftime('%Y-%m-%d %H:%M:%S') if user.last_login_time else None
        })

        return {
            "avatar": user.avatar.url if user.avatar else None,
            "username": user.username,
            "nickname": user.nickname,
            'token': token,
            'roles': role.name if role else '',
            'permissions': permissions
        }
