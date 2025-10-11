from Base.ViewSet import APIViewSet
from apps.campusServices.models import SportPlace, LibraryBook, TransportLine, Notification, WifiHotspot
from apps.campusServices.serializers import SportPlaceSerializer, LibraryBookSerializer, TransportLineSerializer, \
    NotificationSerializer, WifiHotspotSerializer


class SportPlaceViewSet(APIViewSet):
    """体育设施"""
    queryset = SportPlace.objects.all()
    serializer_class = SportPlaceSerializer


class LibraryBookViewSet(APIViewSet):
    """图书馆管理"""
    queryset = LibraryBook.objects.all()
    serializer_class = LibraryBookSerializer


class TransportLineViewSet(APIViewSet):
    """交通管理"""
    queryset = TransportLine.objects.all()
    serializer_class = TransportLineSerializer


class NotificationViewSet(APIViewSet):
    """通知公告"""
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer


class WifiHotspotViewSet(APIViewSet):
    """网络服务"""
    queryset = WifiHotspot.objects.all()
    serializer_class = WifiHotspotSerializer
