from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import UserModel, UserRoleModel, RoleModel, MenuModel
from utils.encrypt import AESHelper
from utils.rules import phone_validator
from utils.generate import generate_random_account

aes_helper = AESHelper()


def password_validator(value):
    if len(value) < 6:
        raise serializers.ValidationError("密码长度不能小于6位")
    return value


class RegisterSerializer(serializers.ModelSerializer):
    """注册请求入参序列化"""
    # 单独配置username，因为在model层的unique执行顺序优先于序列化，导致自定义校验失效
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=UserModel.objects.all(), message='用户名已存在')]
    )
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = UserModel
        fields = ['username', 'password', 'confirm_password']
        extra_kwargs = {
            'password': {
                'write_only': True,  # write_only=True表示该字段只用于反序列化，不用于序列化
                'error_messages': {
                    'blank': '密码不能为空'
                },
                'validators': [password_validator]
            },
            'confirm_password': {
                'error_messages': {
                    'blank': '确认密码不能为空'
                }
            }
        }

    def validate_confirm_password(self, value):
        if not value:
            raise serializers.ValidationError({
                'password': '确认密码是必填项'
            })
        if value != self.initial_data.get('password'):
            raise serializers.ValidationError("两次密码不一致")
        return value

    def create(self, validated_data):
        # 移除 confirm_password，因为它不需要保存到数据库
        validated_data.pop('confirm_password')
        # 对密码进行加密处理
        validated_data['password'] = aes_helper.aes_encrypt(validated_data['password'])
        # 添加默认账号和昵称
        if not validated_data.get('account'):
            validated_data['account'] = generate_random_account()
        if not validated_data.get('nickname'):
            validated_data['nickname'] = generate_random_account()
        # 创建用户
        user = UserModel.objects.create(**validated_data)
        # 添加默认角色
        default_role = RoleModel.objects.get(code='normal_user')
        UserRoleModel.objects.create(user=user, role=default_role)

        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(
        required=False,
        write_only=True,
        error_messages={'blank': '密码不能为空'}
    )
    code = serializers.CharField(
        required=False,
        write_only=True,
        error_messages={'blank': '验证码不能为空'}
    )

    def validate(self, attrs):
        """参数校验"""
        # 检查登录方式是否明确
        if not attrs.get('username') and not attrs.get('phone'):
            raise serializers.ValidationError("必须提供用户名或手机号")
        # 检查登录方式是否冲突
        if attrs.get('username') and attrs.get('phone'):
            raise serializers.ValidationError("不能同时使用用户名和手机号登录")
        # 用户名+密码登录验证
        if attrs.get('username'):
            if not attrs.get('password'):
                raise serializers.ValidationError({"password": "密码不能为空"})
            # 可以添加额外的用户名格式验证
            if len(attrs['username']) < 3:
                raise serializers.ValidationError({"username": "用户名至少3个字符"})
        # 手机号+验证码登录验证
        if attrs.get('phone'):
            if not attrs.get('code'):
                raise serializers.ValidationError({"code": "验证码不能为空"})
            # 验证手机号格式
            if not phone_validator(attrs['phone']):
                raise serializers.ValidationError({"phone": "手机号格式不正确"})
            if len(attrs.get('code')) != 6:
                raise serializers.ValidationError({"code": "验证码格式不正确"})
            # 验证码有效性检查
            # if not check_sms_code(attrs['phone'], attrs['code']):
            #     raise ValidationError({"code": "验证码错误或已过期"})
        return attrs


class TreeMenuSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = MenuModel
        fields = ['id', 'name', 'code', 'path', 'component', 'title', 'icon', 'order', 'type', 'visible', 'parent',
                  'children']

    def get_children(self, obj):
        """动态决定children值"""
        if obj.children.exists():
            return TreeMenuSerializer(obj.children.all(), many=True).data
        return []


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = [
            'id',
            'username',
            'nickname',
            'avatar',
            'phone',
            'email',
            'description',
            'signature',
            'last_login_time'
        ]
        extra_kwargs = {
            'last_login_time': {'read_only': True}
        }

    def to_representation(self, instance):
        """处理头像URL"""
        ret = super().to_representation(instance)
        if ret['avatar']:
            ret['avatar'] = self.context['request'].build_absolute_uri(ret['avatar'])
        return ret

    def validate(self, attrs):
        if self.instance and self.instance.id != self.context['request'].user_id:
            raise serializers.ValidationError("无权修改他人信息")
        return attrs
