from Base.Model import BaseModel
from django.db import models
from apps.oauth.models import UserModel, UserRoleModel
from apps.userManage.models import DepartmentModel


# /* ========================= 教务管理 ========================= */
# DROP TABLE IF EXISTS ac_course;
# CREATE TABLE ac_course (
#   id            BIGINT PRIMARY KEY AUTO_INCREMENT,
#   code          VARCHAR(64)  NOT NULL UNIQUE,
#   name          VARCHAR(128) NOT NULL,
#   credit        DECIMAL(4,1) NOT NULL DEFAULT 0,
#   hours         INT          NOT NULL DEFAULT 0,
#   department_id BIGINT       NULL,
#   created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
#   updated_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
#   INDEX idx_dept (department_id)
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
#
# DROP TABLE IF EXISTS ac_classroom;
# CREATE TABLE ac_classroom (
#   id            BIGINT PRIMARY KEY AUTO_INCREMENT,
#   building      VARCHAR(64)  NOT NULL,
#   room_no       VARCHAR(64)  NOT NULL,
#   capacity      INT          NOT NULL DEFAULT 0,
#   status        TINYINT      NOT NULL DEFAULT 1,
#   created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
#   updated_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
#   UNIQUE uk_room (building, room_no)
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
#
# DROP TABLE IF EXISTS ac_schedule;
# CREATE TABLE ac_schedule (
#   id            BIGINT PRIMARY KEY AUTO_INCREMENT,
#   course_id     BIGINT       NOT NULL,              -- ac_course
#   teacher_id    BIGINT       NOT NULL,              -- sc_teacher
#   classroom_id  BIGINT       NOT NULL,              -- ac_classroom
#   week_day      TINYINT      NOT NULL,              -- 1-7
#   start_time    TIME         NOT NULL,
#   end_time      TIME         NOT NULL,
#   start_date    DATE         NOT NULL,
#   end_date      DATE         NOT NULL,
#   created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
#   updated_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
#   INDEX idx_course (course_id),
#   INDEX idx_teacher (teacher_id)
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
#
# DROP TABLE IF EXISTS ac_exam;
# CREATE TABLE ac_exam (
#   id            BIGINT PRIMARY KEY AUTO_INCREMENT,
#   course_id     BIGINT       NOT NULL,
#   exam_date     DATETIME     NOT NULL,
#   classroom_id  BIGINT       NULL,
#   type          VARCHAR(32)  NOT NULL DEFAULT 'final', -- 期末/期中/随堂
#   remark        VARCHAR(255) NULL,
#   created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
#   updated_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
#   INDEX idx_course (course_id)
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

# -- 课程
# INSERT INTO ac_course (code, name, credit, hours, department_id)
# VALUES ('CS101','程序设计基础',3.0,48,1),
#        ('CS201','数据结构',3.5,64,1);
#
# -- 教室
# INSERT INTO ac_classroom (building, room_no, capacity, status)
# VALUES ('A楼','201',60,1),('A楼','305',80,1);
#
# -- 课程表
# INSERT INTO ac_schedule (course_id, teacher_id, classroom_id, week_day, start_time, end_time, start_date, end_date)
# VALUES (1,1,1,2,'08:00:00','09:35:00','2024-09-01','2024-12-31'),
#        (2,2,2,4,'10:00:00','11:35:00','2024-09-01','2024-12-31');
#
# -- 考试
# INSERT INTO ac_exam (course_id, exam_date, classroom_id, type, remark)
# VALUES (1,'2024-12-20 09:00:00',1,'final','闭卷'),
#        (2,'2024-12-22 14:00:00',2,'final','开卷');


class Course(BaseModel):
    """课程表"""
    COURSE_TYPE_CHOICES = (
        ('compulsory', '必修课'),
        ('elective', '选修课'),
        ('practice', '实践课'),
    )

    id = models.AutoField(primary_key=True, verbose_name="课程ID")
    code = models.CharField(max_length=64, unique=True, verbose_name="课程代码")
    name = models.CharField(max_length=128, verbose_name="课程名称")
    credit = models.DecimalField(max_digits=4, decimal_places=1, default=0, verbose_name="学分")
    hours = models.IntegerField(default=0, verbose_name="学时")
    course_type = models.CharField(max_length=32, choices=COURSE_TYPE_CHOICES, default='compulsory',
                                   verbose_name="课程类型")
    department = models.ForeignKey(DepartmentModel, on_delete=models.SET_NULL, null=True, blank=True,
                                   verbose_name="开课部门")
    description = models.TextField(null=True, blank=True, verbose_name="课程描述")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "ac_course"
        verbose_name = "课程"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.code} - {self.name}"


class Classroom(BaseModel):
    """教室表"""
    CLASSROOM_TYPE_CHOICES = (
        ('normal', '普通教室'),
        ('multimedia', '多媒体教室'),
        ('lab', '实验室'),
        ('computer', '计算机房'),
    )

    STATUS_CHOICES = (
        (1, '可用'),
        (0, '禁用'),
        (2, '维修中'),
    )

    id = models.AutoField(primary_key=True, verbose_name="教室ID")
    building = models.CharField(max_length=64, verbose_name="楼栋")
    room_no = models.CharField(max_length=64, verbose_name="房间号")
    capacity = models.IntegerField(default=0, verbose_name="容量")
    classroom_type = models.CharField(max_length=32, choices=CLASSROOM_TYPE_CHOICES, default='normal',
                                      verbose_name="教室类型")
    equipment = models.TextField(null=True, blank=True, verbose_name="设备信息")
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="状态")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "ac_classroom"
        verbose_name = "教室"
        verbose_name_plural = verbose_name
        unique_together = ['building', 'room_no']

    def __str__(self):
        return f"{self.building}-{self.room_no}"


class Schedule(BaseModel):
    """课程安排表"""
    WEEK_DAY_CHOICES = (
        (1, '星期一'),
        (2, '星期二'),
        (3, '星期三'),
        (4, '星期四'),
        (5, '星期五'),
        (6, '星期六'),
        (7, '星期日'),
    )

    id = models.AutoField(primary_key=True, verbose_name="课程表ID")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name="课程")
    teacher = models.ForeignKey(UserRoleModel, on_delete=models.CASCADE, verbose_name="教师",
                                limit_choices_to={'role_id': 2})  # 限制只能选择教师角色
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, verbose_name="教室")
    week_day = models.IntegerField(choices=WEEK_DAY_CHOICES, verbose_name="星期几")
    start_time = models.TimeField(verbose_name="开始时间")
    end_time = models.TimeField(verbose_name="结束时间")
    start_date = models.DateField(verbose_name="开始日期")
    end_date = models.DateField(verbose_name="结束日期")
    semester = models.CharField(max_length=32, default='2024-2025-1', verbose_name="学期")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "ac_schedule"
        verbose_name = "课程安排"
        verbose_name_plural = verbose_name
        indexes = [
            models.Index(fields=['course', 'teacher']),
            models.Index(fields=['week_day', 'start_time']),
            models.Index(fields=['semester']),
        ]

    def __str__(self):
        return f"{self.course.name} - {self.get_week_day_display()} {self.start_time}"


class Exam(BaseModel):
    """考试表"""
    EXAM_TYPE_CHOICES = (
        ('final', '期末考试'),
        ('midterm', '期中考试'),
        ('quiz', '随堂测验'),
        ('makeup', '补考'),
    )

    id = models.AutoField(primary_key=True, verbose_name="考试ID")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name="课程")
    exam_date = models.DateTimeField(verbose_name="考试时间")
    classroom = models.ForeignKey(Classroom, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="考场")
    exam_type = models.CharField(max_length=32, choices=EXAM_TYPE_CHOICES, default='final', verbose_name="考试类型")
    duration = models.IntegerField(default=120, verbose_name="考试时长(分钟)")
    supervisor = models.ForeignKey(UserRoleModel, on_delete=models.SET_NULL, null=True, blank=True,
                                   limit_choices_to={'role_id': 2}, verbose_name="监考老师")
    remark = models.TextField(null=True, blank=True, verbose_name="备注")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "ac_exam"
        verbose_name = "考试"
        verbose_name_plural = verbose_name
        indexes = [
            models.Index(fields=['course', 'exam_date']),
        ]

    def __str__(self):
        return f"{self.course.name} - {self.get_exam_type_display()}"


class CourseTeacher(BaseModel):
    """课程教师关联表"""
    id = models.AutoField(primary_key=True, verbose_name="ID")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name="课程")
    teacher = models.ForeignKey(UserRoleModel, on_delete=models.CASCADE, verbose_name="教师",
                                limit_choices_to={'role_id': 2})
    role = models.CharField(max_length=32, default='主讲教师', verbose_name="角色")  # 主讲教师/辅导教师
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "ac_course_teacher"
        verbose_name = "课程教师"
        verbose_name_plural = verbose_name
        unique_together = ['course', 'teacher']


class StudentCourse(BaseModel):
    """学生选课表"""
    STATUS_CHOICES = (
        ('selected', '已选课'),
        ('studying', '修读中'),
        ('completed', '已修完'),
        ('dropped', '已退课'),
    )

    id = models.AutoField(primary_key=True, verbose_name="ID")
    student = models.ForeignKey(UserRoleModel, on_delete=models.CASCADE, verbose_name="学生",
                                limit_choices_to={'role_id': 3})
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name="课程")
    semester = models.CharField(max_length=32, verbose_name="学期")
    select_time = models.DateTimeField(auto_now_add=True, verbose_name="选课时间")
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default='selected', verbose_name="选课状态")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "ac_student_course"
        verbose_name = "学生选课"
        verbose_name_plural = verbose_name
        unique_together = ['student', 'course', 'semester']
