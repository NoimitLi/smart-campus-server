from rest_framework import routers
from apps.logisticalSupport.views import FacilityViewSet, MaintenanceViewSet, CleaningTaskViewSet, CanteenMenuViewSet, \
    SecurityEventViewSet

route = routers.DefaultRouter()
route.register('facility', FacilityViewSet)  # 设施管理
route.register('maintenance', MaintenanceViewSet)  # 维修管理
route.register('cleaningTask', CleaningTaskViewSet)  # 保洁管理
route.register('canteenMenu', CanteenMenuViewSet)  # 食堂菜单
route.register('securityEvent', SecurityEventViewSet)  # 安全管理

urlpatterns = route.urls
