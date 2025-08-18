"""
URL configuration for SmartCampusServer project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# 配置 API 文档基本信息
schema_view = get_schema_view(
    openapi.Info(
        title="项目 API",
        default_version='v1',
        description="API 接口文档描述",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],  # 允许任何人访问文档
)

urlpatterns = [
    # 文档 JSON/YAML 下载
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    # Swagger UI 页面
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    # ReDoc 页面
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/admin/', admin.site.urls),
    path('api/auth/', include('authSystem.urls')),  # 两端的认证系统
    path('api/as/', include('adminServer.urls')),  # adminServer的URL配置
    path('api/ss/', include('StudentServer.urls')),  # StudentServer的URL配置
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
