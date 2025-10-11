from rest_framework import routers
from apps.systemMonitoring.views import LoginLogViewSet, OperationLogViewSet, OnlineUserViewSet, ServerMetricViewSet

route = routers.DefaultRouter()

route.register(r'loginLog', LoginLogViewSet)  # 登录日志
route.register(r'operationLog', OperationLogViewSet)  # 操作日志
route.register(r'onlineUser', OnlineUserViewSet)  # 在线用户
route.register(r'serverMetric', ServerMetricViewSet)  # 服务器指标

urlpatterns = route.urls
