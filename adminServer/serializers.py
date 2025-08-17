from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from authSystem.models import RoleModel
from .models import DepartmentModel


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
            'created_time': {'read_only': True},  # 自动生成，只读
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
