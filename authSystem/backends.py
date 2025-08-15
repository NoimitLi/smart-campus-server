"""
在settings.py中配置AUTHENTICATION_BACKENDS
"""
from django.contrib.auth.backends import ModelBackend
from .models import UserModel, UserRoleModel, RolePermissionModel
from django.db.models import Q


class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            mode = kwargs.get('mode')
            user = None
            # 用户名登录
            if mode == 'account':
                user = UserModel.objects.get(Q(username=username) | Q(account=username))
                if not user.check_password(password):
                    return None
            # 手机号登录
            elif mode == 'phone':
                user = UserModel.objects.get(Q(phone=kwargs.get('phone')))
                # 这里应该添加验证码验证逻辑
            else:
                return None
            # 更新最后登录时间
            user.save(update_fields=['last_login_time'])
            return user
        except UserModel.DoesNotExist:
            return None
