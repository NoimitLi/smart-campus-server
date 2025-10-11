from rest_framework import routers
from apps.studentServer.views import ActivityViewSet, GradeViewSet, AttendanceViewSet

route = routers.DefaultRouter()

route.register(r'activity', ActivityViewSet, basename='activity')  # 活动管理
route.register(r'grade', GradeViewSet, basename='grade')  # 成绩管理
route.register(r'attendance', AttendanceViewSet, basename='attendance')  # 考勤管理

urlpatterns = route.urls
