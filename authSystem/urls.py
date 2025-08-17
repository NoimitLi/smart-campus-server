from django.urls import path
from . import views

app_name = 'authSystem'

urlpatterns = [
    path('register', views.RegisterView.as_view(), name='register'),  # 注册
    path('send_code/<str:phone>', views.SendCode.as_view(), name='send_code'),
    path('login', views.LoginView.as_view(), name='login'),  # 登录
    path('refresh', views.TokenRefreshView.as_view(), name='refresh'),  # 刷新token
    path('logout', views.LogoutView.as_view(), name='logout'),  # 登出
    path('menus', views.MenuView.as_view(), name='menu'),  # 菜单
    path('mine', views.MineView.as_view(), name='mine')  # 个人中心
]
