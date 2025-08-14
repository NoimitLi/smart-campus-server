from rest_framework import serializers
from .models import UserModel


class RegisterSerializer(serializers.ModelSerializer):
    """注册请求入参序列化"""
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = UserModel
        fields = ['username', 'password', 'confirm_password']
        # extra_kwargs = {
        #     'password': {'write_only': True},
        # }

    def validated_username(self, value):
        if UserModel.objects.filter(username=value).exists():
            raise serializers.ValidationError("用户名已存在")
        return value

    def validate_password(self, value):
        if len(value) < 6:
            raise serializers.ValidationError("密码长度不能小于6位")
        return value

    def validate_confirm_password(self, value):
        if value != self.initial_data.get('password'):
            raise serializers.ValidationError("两次密码不一致")
        return value

    # def validate(self, data):
    #     """验证两次输入的密码是否一致"""
    #     if data['password'] != data['confirm_password']:
    #         raise serializers.ValidationError("两次输入的密码不一致")
    #     return data

    def create(self, validated_data):
        # 移除 confirm_password，因为它不需要保存到数据库
        validated_data.pop('confirm_password')
        # 对密码进行哈希处理
        # validated_data['password'] = make_password(validated_data['password'])
        # return UserModel.objects.create(**validated_data)
