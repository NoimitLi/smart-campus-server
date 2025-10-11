from rest_framework import routers
from apps.campusServices.views import SportPlaceViewSet, LibraryBookViewSet, TransportLineViewSet, NotificationViewSet, \
    WifiHotspotViewSet

route = routers.DefaultRouter()

route.register(r'sportPlace', SportPlaceViewSet)  # 体育设施
route.register(r'libraryBook', LibraryBookViewSet)  # 图书馆书籍
route.register(r'transportLine', TransportLineViewSet)  # 交通服务
route.register(r'notification', NotificationViewSet)  # 通知公告
route.register(r'wifiHotspot', WifiHotspotViewSet)  # 网络服务

urlpatterns = route.urls
