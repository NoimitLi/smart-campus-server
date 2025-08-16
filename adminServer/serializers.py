from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from authSystem.models import RoleModel


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
