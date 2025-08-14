from django.urls import path
from . import views

app_name = 'authSystem'

urlpatterns = [
    path('register', views.RegisterView.as_view(), name='register'),  # 注册
    path('login', views.LoginView.as_view(), name='login'),  # 登录
    path('logout', views.LogoutView.as_view(), name='logout'),  # 登出
    path('mine/<str:user_id>', views.MineView.as_view(), name='mine'),  # 个人中心
]
