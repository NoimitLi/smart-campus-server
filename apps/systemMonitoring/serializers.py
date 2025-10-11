from rest_framework import serializers
from apps.systemMonitoring.models import LoginLog, OperationLog, OnlineUser, ServerMetric


class LoginLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginLog
        fields = '__all__'


class OperationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperationLog
        fields = '__all__'


class OnlineUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnlineUser
        fields = '__all__'


class ServerMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServerMetric
        fields = '__all__'
