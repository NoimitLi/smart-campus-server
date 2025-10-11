from django.db import models
from Base.Model import BaseModel
from apps.userManage.models import UserModel
from apps.academicManagement.models import Course


# /* ========================= 学生服务 ========================= */
# DROP TABLE IF EXISTS st_attendance;
# CREATE TABLE st_attendance (
#   id            BIGINT PRIMARY KEY AUTO_INCREMENT,
#   student_id    BIGINT       NOT NULL,
#   course_id     BIGINT       NOT NULL,
#   check_date    DATE         NOT NULL,
#   status        VARCHAR(16)  NOT NULL,              -- present/absent/late
#   remark        VARCHAR(255) NULL,
#   created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
#   INDEX idx_stu (student_id),
#   INDEX idx_course (course_id)
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
#
# DROP TABLE IF EXISTS st_grade;
# CREATE TABLE st_grade (
#   id            BIGINT PRIMARY KEY AUTO_INCREMENT,
#   student_id    BIGINT       NOT NULL,
#   course_id     BIGINT       NOT NULL,
#   score         DECIMAL(5,2) NOT NULL,
#   grade_point   DECIMAL(3,2) NULL,
#   term          VARCHAR(32)  NOT NULL,              -- 2024-2025-1
#   created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
#   INDEX idx_stu (student_id),
#   INDEX idx_course (course_id)
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
#
# DROP TABLE IF EXISTS st_activity;
# CREATE TABLE st_activity (
#   id            BIGINT PRIMARY KEY AUTO_INCREMENT,
#   title         VARCHAR(128) NOT NULL,
#   category      VARCHAR(64)  NOT NULL,             -- 比赛/讲座/社团
#   place         VARCHAR(128) NULL,
#   start_time    DATETIME     NOT NULL,
#   end_time      DATETIME     NOT NULL,
#   organizer     VARCHAR(128) NULL,
#   description   TEXT         NULL,
#   created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

class Attendance(BaseModel):
    """考勤表"""
    id = models.AutoField(primary_key=True, verbose_name='记录id')
    student = models.ForeignKey(UserModel, on_delete=models.CASCADE, verbose_name='学生')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='课程')
    check_date = models.DateField(verbose_name='签到日期')
    status = models.CharField(max_length=16, verbose_name='签到状态')
    remark = models.CharField(max_length=255, null=True, verbose_name='备注')

    class Meta:
        db_table = 'st_attendance'
        verbose_name = '学生考勤表'
        verbose_name_plural = verbose_name


class Grade(BaseModel):
    """成绩表"""
    id = models.AutoField(primary_key=True, verbose_name='记录id')
    student = models.ForeignKey(UserModel, on_delete=models.CASCADE, verbose_name='学生')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='课程')
    score = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='成绩')
    grade_point = models.DecimalField(max_digits=3, decimal_places=2, null=True, verbose_name='绩点')
    term = models.CharField(max_length=32, verbose_name='学期')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'st_grade'
        verbose_name = '学生成绩表'
        verbose_name_plural = verbose_name


class Activity(BaseModel):
    """活动表"""
    id = models.AutoField(primary_key=True, verbose_name='记录id')
    title = models.CharField(max_length=128, verbose_name='活动标题')
    category = models.CharField(max_length=64, verbose_name='活动类别')
    place = models.CharField(max_length=128, null=True, verbose_name='活动地点')
    start_time = models.DateTimeField(verbose_name='活动开始时间')
    end_time = models.DateTimeField(verbose_name='活动结束时间')
    organizer = models.CharField(max_length=128, null=True, verbose_name='活动组织者')
    description = models.TextField(null=True, verbose_name='活动描述')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'st_activity'
        verbose_name = '学生活动表'
        verbose_name_plural = verbose_name
