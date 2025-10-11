from Base.ViewSet import APIViewSet
from apps.studentServer.models import Activity, Grade, Attendance
from apps.studentServer.serializers import ActivitySerializer, GradeSerializer, AttendanceSerializer


class ActivityViewSet(APIViewSet):
    """活动管理"""
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer


class GradeViewSet(APIViewSet):
    """成绩管理"""
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer


class AttendanceViewSet(APIViewSet):
    """考勤管理"""
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
