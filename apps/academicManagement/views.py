from Base.ViewSet import APIViewSet
from apps.academicManagement.models import Course, Classroom, Schedule, Exam
from apps.academicManagement.serializers import CourseSerializer, ClassroomSerializer, ScheduleSerializer, \
    ExamSerializer


# Create your views here.

class CourseViewSet(APIViewSet):
    """课程管理"""
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class ClassRoomViewSet(APIViewSet):
    """教室管理"""
    queryset = Classroom.objects.all()
    serializer_class = ClassroomSerializer


class ScheduleViewSet(APIViewSet):
    """课表管理"""
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer


class ExamViewSet(APIViewSet):
    """考试管理"""
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
