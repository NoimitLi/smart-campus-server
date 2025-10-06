from django.urls import path, include
from .views import RoleViewSet, DepartmentViewSet, UserViewSet
from rest_framework.routers import DefaultRouter

app_name = 'userManage'

router = DefaultRouter()
router.register(r'role', RoleViewSet, basename='role')
router.register(r'department', DepartmentViewSet, basename='department')
router.register(r'user', UserViewSet, basename='user')

urlpatterns = router.urls
