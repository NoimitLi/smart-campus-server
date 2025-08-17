from django.urls import path, include
from .views import RoleViewSet, DepartmentViewSet
from rest_framework.routers import DefaultRouter

app_name = 'adminServer'

router = DefaultRouter()
router.register(r'role', RoleViewSet, basename='role')
router.register(r'department', DepartmentViewSet, basename='department')
urlpatterns = router.urls
