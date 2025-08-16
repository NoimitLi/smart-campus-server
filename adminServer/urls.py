from django.urls import path, include
from .views import RoleViewSet
from rest_framework.routers import DefaultRouter

app_name = 'adminServer'

router = DefaultRouter()
router.register(r'role', RoleViewSet, basename='role')
urlpatterns = router.urls
