from Base.ViewSet import APIViewSet
from apps.logisticalSupport.models import Facility, Maintenance, CleaningTask, CanteenMenu, SecurityEvent
from apps.logisticalSupport.serializers import FacilitySerializer, MaintenanceSerializer, CleaningTaskSerializer, \
    CanteenMenuSerializer, SecurityEventSerializer


class FacilityViewSet(APIViewSet):
    """设施管理"""
    queryset = Facility.objects.all()
    serializer_class = FacilitySerializer


class MaintenanceViewSet(APIViewSet):
    """维修管理"""
    queryset = Maintenance.objects.all()
    serializer_class = MaintenanceSerializer


class CleaningTaskViewSet(APIViewSet):
    """保洁管理"""
    queryset = CleaningTask.objects.all()
    serializer_class = CleaningTaskSerializer


class CanteenMenuViewSet(APIViewSet):
    """食堂菜单管理"""
    queryset = CanteenMenu.objects.all()
    serializer_class = CanteenMenuSerializer


class SecurityEventViewSet(APIViewSet):
    """安全管理"""
    queryset = SecurityEvent.objects.all()
    serializer_class = SecurityEventSerializer
