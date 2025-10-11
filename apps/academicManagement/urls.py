from rest_framework import routers
from apps.academicManagement.views import CourseViewSet, ClassRoomViewSet, ScheduleViewSet, ExamViewSet

route = routers.DefaultRouter()

route.register(r'course', CourseViewSet)  # 课程管理
route.register(r'classroom', ClassRoomViewSet)  # 教室管理
route.register(r'schedule', ScheduleViewSet)  # 课表管理
route.register(r'exam', ExamViewSet)  # 考试管理

urlpatterns = route.urls
