from datetime import timedelta
from django.contrib.auth import authenticate
from django.utils import timezone
from django.core.cache import cache
from authSystem.services.sms import SmsService
from core.exceptions import AuthFailed, TokenInvalid
from authSystem.models import UserRoleModel, RolePermissionModel
from utils.token import generate_token, verify_token


class AuthController:
    """认证业务控制器 - 优化版"""

    ACCESS_TOKEN_EXPIRE = timedelta(hours=2)  # Access Token 2小时过期
    REFRESH_TOKEN_EXPIRE = timedelta(days=7)  # Refresh Token 7天过期
    SLIDING_EXPIRE = timedelta(days=7)  # 滑动过期窗口7天

    def __init__(self):
        self.cache = cache

    def login(self, data: dict):
        """统一登录处理"""
        try:
            # 分发登录方式
            if 'username' in data:
                return self._account_login(data['username'], data['password'])
            else:
                return self._phone_login(data['phone'], data['code'])
        except Exception as e:
            raise AuthFailed(str(e))

    def _account_login(self, username: str, password: str):
        """账号密码登录"""
        user = authenticate(username=username, password=password, mode='account')
        if not user:
            raise AuthFailed('账号或密码错误')
        return self._generate_auth_result(user)

    def _phone_login(self, phone: str, code: str):
        """手机号登录"""
        if not SmsService().verify_sms_code(phone, code):
            raise AuthFailed('验证码错误')

        user = authenticate(phone=phone, code=code, mode='phone')
        if not user:
            raise AuthFailed('手机号未注册')

        return self._generate_auth_result(user)

    def _generate_auth_result(self, user):
        """生成认证结果(双Token)"""
        # 更新最后活动时间(用于滑动过期)
        user.last_login_time = timezone.now()
        user.save(update_fields=['last_login_time'])

        # 获取用户权限信息
        user_info = self._get_user_info(user)
        # 生成令牌
        tokens = self.generate_tokens(user)

        return {
            'user': user_info,
            'access_token': tokens['access_token'],
            'refresh_token': tokens['refresh_token']
        }

    def _get_user_role(self, user):
        try:
            user_role = UserRoleModel.objects.get(user=user.id)
            role = user_role.role
        except UserRoleModel.DoesNotExist:
            role = None

        # 将角色信息挂载到user中
        setattr(user, 'role', role)
        return role

    def _get_user_info(self, user):
        """获取用户角色和权限信息"""
        role = self._get_user_role(user)

        permissions = []
        if role:
            role_permissions = RolePermissionModel.objects.filter(role=role.id)
            permissions = [rp.permission.code for rp in role_permissions]

        return {
            "avatar": user.avatar.url if user.avatar else None,
            "username": user.username,
            "nickname": user.nickname,
            'roles': role.name if role else '',
            'permissions': permissions
        }

    def generate_access_token(self, user):
        if not getattr(user, 'role', ''):
            self._get_user_role(user)

        # Access Token包含更多用户信息
        access_payload = {
            'user_id': user.id,
            'username': user.username,
            'role_id': getattr(user.role, 'id', ''),
            'last_login': user.last_login_time.isoformat() if user.last_login_time else None,
            'token_type': 'access'
        }
        access_token = generate_token(
            data=access_payload,
            expire=self.ACCESS_TOKEN_EXPIRE
        )
        return access_token

    def generate_refresh_token(self, user):
        # Refresh Token只包含必要信息
        refresh_payload = {
            'user_id': user.id,
            'token_type': 'refresh'
        }

        refresh_token = generate_token(
            data=refresh_payload,
            expire=self.REFRESH_TOKEN_EXPIRE
        )

        # 将refresh_token存入缓存，用于校验和滑动过期控制
        self.cache.set(
            f'refresh_token:{user.id}',
            refresh_token,
            timeout=int(self.SLIDING_EXPIRE.total_seconds())
        )
        return refresh_token

    def generate_tokens(self, user):
        """生成双Token"""
        access_token = self.generate_access_token(user)
        refresh_token = self.generate_refresh_token(user)

        return {
            'access_token': access_token,
            'refresh_token': refresh_token
        }

    def refresh_token(self, refresh_token: str):
        """刷新Access Token"""
        try:
            # 验证refresh_token有效性
            payload = verify_token(refresh_token)
            if payload.get('token_type') != 'refresh':
                raise TokenInvalid('无效的Token类型')

            user_id = payload['user_id']

            # 检查缓存中的refresh_token是否匹配(防止被盗用)
            cached_refresh = self.cache.get(f'refresh_token:{user_id}')
            if cached_refresh != refresh_token:
                raise TokenInvalid('Refresh Token已失效')

            # 检查用户最后活动时间是否在滑动窗口内
            from ..models import UserModel
            user = UserModel.objects.get(id=user_id)
            if timezone.now() - user.last_login_time > self.SLIDING_EXPIRE:
                raise TokenInvalid('长时间未活动，请重新登录')

            # 更新最后活动时间(实现滑动过期)
            user.last_login_time = timezone.now()
            user.save(update_fields=['last_login_time'])

            # 更新redis缓存中的token过期时间
            self.cache.expire(f'refresh_token:{user.id}', self.REFRESH_TOKEN_EXPIRE)

            # 生成新的access_token
            return {
                'access_token': self.generate_access_token(user)
            }

        except Exception as e:
            raise TokenInvalid(str(e))

    def logout(self, user_id: int):
        """登出处理"""
        # 清除refresh_token缓存
        self.cache.delete(f'refresh_token:{user_id}')
        return True
