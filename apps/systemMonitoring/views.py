from Base.ViewSet import APIViewSet
from apps.systemMonitoring.models import LoginLog, OperationLog, OnlineUser, ServerMetric
from apps.systemMonitoring.serializers import LoginLogSerializer, OperationLogSerializer, OnlineUserSerializer, \
    ServerMetricSerializer


class LoginLogViewSet(APIViewSet):
    """登录日志"""
    queryset = LoginLog.objects.all()
    serializer_class = LoginLogSerializer


class OperationLogViewSet(APIViewSet):
    """操作日志"""
    queryset = OperationLog.objects.all()
    serializer_class = OperationLogSerializer


class OnlineUserViewSet(APIViewSet):
    """在线用户"""
    queryset = OnlineUser.objects.all()
    serializer_class = OnlineUserSerializer


class ServerMetricViewSet(APIViewSet):
    """服务器指标"""
    queryset = ServerMetric.objects.all()
    serializer_class = ServerMetricSerializer
