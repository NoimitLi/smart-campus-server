import os
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.core.validators import RegexValidator
from authSystem.models import RoleModel, UserModel, UserRoleModel
from authSystem.serializers import RegisterSerializer
from .models import DepartmentModel, UserDepartmentModel
from utils.encrypt import AESHelper

aes_helper = AESHelper()


class RoleSerializer(serializers.ModelSerializer):
    # 对code字段添加唯一性验证
    code = serializers.CharField(
        required=True,
        error_messages={'required': '标识是必填字段'},
        validators=[UniqueValidator(queryset=RoleModel.objects.all(), message='标识已存在')]
    )
    # 对name字段添加必填验证
    name = serializers.CharField(
        required=True,
        error_messages={'required': '名称是必填字段'},
        validators=[UniqueValidator(queryset=RoleModel.objects.all(), message='名称已存在')]
    )

    class Meta:
        model = RoleModel
        fields = '__all__'
        extra_kwargs = {
            # 'name': {'required': True, 'error_messages': {'required': '名称是必填字段'}},  # 名称必填
            # 'code': {'required': True},  # 标识必填
            'description': {'required': False, 'allow_blank': True},
            'status': {'required': False},
            'create_time': {'read_only': True},  # 自动生成，只读
            'update_time': {'read_only': True},  # 自动生成，只读
        }

    def validate(self, attrs):
        return attrs

    def update(self, instance, validated_data):
        # print(validated_data)
        return super().update(instance, validated_data)

    def create(self, validated_data):
        # return RoleModel.objects.create(**validated_data)
        return super().create(validated_data)


class DepartmentSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    parent_name = serializers.CharField(
        source='parent.name',
        read_only=True,
        help_text='上级部门名称'
    )

    class Meta:
        model = DepartmentModel
        fields = [
            'id', 'name', 'code', 'parent', 'parent_name', 'order',
            'leader', 'phone', 'email', 'status', 'description',
            'updated_time', 'create_time', 'children'
        ]
        extra_kwargs = {
            'parent': {'required': False},
            'order': {'required': False, 'default': 0},
            'status': {'required': False, 'default': True}
        }

    def get_children(self, obj):
        """递归获取子部门（优化查询）"""
        children = obj.children.all().order_by('order')
        if children.exists():
            return DepartmentSerializer(children, many=True).data
        return []

    def validate(self, data):
        """验证业务规则"""
        instance = getattr(self, 'instance', None)
        parent = data.get('parent', instance.parent if instance else None)
        name = data.get('name', instance.name if instance else None)

        # 验证同级部门名称唯一性
        if name and parent:
            qs = DepartmentModel.objects.filter(parent=parent, name=name)
            print(instance)
            if instance:
                qs = qs.exclude(pk=instance.pk)
            if qs.exists():
                raise serializers.ValidationError({
                    'name': f'同级部门下已存在名为 {name} 的部门'
                })

        return data

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    confirm_password = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = UserModel
        fields = '__all__'
        extra_kwargs = {
            'username': {
                'required': True,
                'validators': [
                    RegexValidator(
                        regex=r'^[\w.@+-]+$',
                        message='用户名只能包含字母、数字和@/./+/-/_'
                    ),
                    UniqueValidator(UserModel.objects.all(), message='用户名已存在')
                ],

            },
            'phone': {
                'required': False,
                'validators': [
                    RegexValidator(
                        regex=r'^1[3-9]\d{9}$',
                        message='请输入有效的手机号码'
                    ),
                ]
            },
            'password': {
                'required': False,
                'write_only': True,
            },
            'account': {'required': False},
            'nickname': {'required': False},
            'avatar': {'required': False},
            'email': {'required': False},
            'description': {'required': False},
            'signature': {'required': False},
            'status': {'required': False, 'default': True},
            'create_time': {'read_only': True},  # 自动生成，只读
            'update_time': {'read_only': True},  # 自动生成，只读
        }

    def get_role(self, obj):
        try:
            user_role = UserRoleModel.objects.get(user=obj)
            return {
                'id': user_role.role.id,
                'role': user_role.role.name
            }
        except UserRoleModel.DoesNotExist:
            return None

    def get_department(self, obj):
        try:
            user_dept = UserDepartmentModel.objects.get(user=obj)
            return {
                'id': user_dept.department.id,
                'name': user_dept.department.name,
                'full_path': user_dept.department.get_full_path()
            }
        except UserDepartmentModel.DoesNotExist:
            return None

    def validate_avatar(self, value):
        """验证头像文件"""
        # 检查文件大小（限制为2MB）
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("头像文件大小不能超过2MB")

        # 检查文件类型
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in valid_extensions:
            raise serializers.ValidationError("不支持的文件类型，请上传jpg/png/gif格式图片")

        return value

    def validate(self, attrs):
        return attrs

    def update(self, instance, validated_data):
        if 'password' not in validated_data:
            validated_data.pop('password', None)
        else:
            register = RegisterSerializer(data=validated_data)
            try:
                register.validate_confirm_password(validated_data.get('confirm_password'))
            except serializers.ValidationError as e:
                raise e
            validated_data['password'] = aes_helper.aes_encrypt(validated_data.get('password', '123456'))
        validated_data.pop('last_login_time', None)

        user = super().update(instance, validated_data)

        self.update_role(user)
        self.update_dept(user)

        return user

    def create(self, validated_data):
        # 调用注册接口
        if not validated_data.get('password'):
            raise serializers.ValidationError({
                'password': '创建用户时密码是必填项'
            })
        validated_data['confirm_password'] = validated_data['password']
        register = RegisterSerializer(data=validated_data)
        user = None
        if register.is_valid():
            user = register.save()

        # # 创建用户
        # user = super().create(validated_data)
        self.update_role(user)
        self.update_dept(user)

        return user

    def to_representation(self, instance):
        """hook获取data前的操作"""
        ret = super().to_representation(instance)
        # 将avatar转为完整的url
        if ret['avatar']:
            ret['avatar'] = self.context['request'].build_absolute_uri(ret['avatar'])
            pass
        return ret

    def update_role(self, user):
        """添加或更新角色"""
        if not self.context.get('request'):
            return
        # 添加或更新角色
        try:
            if 'role' in self.context.get('request').data:
                role_id = self.context.get('request').data.get('role')
                role = RoleModel.objects.get(id=role_id)
            else:
                role = RoleModel.objects.get(code='normal_user')
        except RoleModel.DoesNotExist:
            raise serializers.ValidationError({
                'department': '角色不存在'
            })
        try:
            # 修改角色
            user_role = UserRoleModel.objects.get(user=user)
            UserRoleModel.objects.filter(user=user).update(role=role)
        except UserRoleModel.DoesNotExist:
            # 如果原始没有分配，创建
            UserRoleModel.objects.create(user=user, role=role)

    def update_dept(self, user):
        """添加或更新部门"""
        if not self.context.get('request'):
            return
        if 'department' in self.context.get('request').data:
            dept_id = self.context.get('request').data.get('department')
            dept = None
            try:
                dept = DepartmentModel.objects.get(id=dept_id)
                # 修改部门
                user_dept = UserDepartmentModel.objects.get(user=user)
                UserDepartmentModel.objects.filter(user=user).update(department=dept)
            except UserDepartmentModel.DoesNotExist:
                # 如果原始没有分配，创建
                UserDepartmentModel.objects.create(user=user, department=dept)
                # UserDepartmentModel.objects.update_or_create(user=user, department=dept)
            except DepartmentModel.DoesNotExist:
                raise serializers.ValidationError({
                    'department': '部门不存在'
                })
