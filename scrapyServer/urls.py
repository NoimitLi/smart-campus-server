from django.urls import path
from . import views

urlpatterns = [
    path('test/<int:id>', views.TestView.as_view(), name='test'),
]
