from django.db import models
from Base.Model import BaseModel


# /* ========================= 后勤保障 ========================= */
# DROP TABLE IF EXISTS lg_facility;
# CREATE TABLE lg_facility (
#   id            BIGINT PRIMARY KEY AUTO_INCREMENT,
#   name          VARCHAR(128) NOT NULL,             -- 设施名称
#   category      VARCHAR(64)  NOT NULL,             -- 水电/电梯/空调
#   location      VARCHAR(128) NULL,
#   status        VARCHAR(32)  NOT NULL DEFAULT 'normal', -- normal/repair/stop
#   created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
#
# DROP TABLE IF EXISTS lg_maintenance;
# CREATE TABLE lg_maintenance (
#   id            BIGINT PRIMARY KEY AUTO_INCREMENT,
#   facility_id   BIGINT       NOT NULL,
#   reporter      VARCHAR(64)  NULL,
#   description   TEXT         NULL,
#   level         VARCHAR(16)  NOT NULL DEFAULT 'medium', -- low/medium/high
#   status        VARCHAR(16)  NOT NULL DEFAULT 'open',   -- open/processing/done
#   created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
#   updated_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
#   INDEX idx_facility (facility_id)
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
#
# DROP TABLE IF EXISTS lg_canteen_menu;
# CREATE TABLE lg_canteen_menu (
#   id            BIGINT PRIMARY KEY AUTO_INCREMENT,
#   canteen       VARCHAR(64)  NOT NULL,
#   dish_name     VARCHAR(128) NOT NULL,
#   price         DECIMAL(6,2) NOT NULL,
#   tags          VARCHAR(128) NULL,
#   created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
#
# DROP TABLE IF EXISTS lg_security_event;
# CREATE TABLE lg_security_event (
#   id            BIGINT PRIMARY KEY AUTO_INCREMENT,
#   title         VARCHAR(128) NOT NULL,
#   event_time    DATETIME     NOT NULL,
#   place         VARCHAR(128) NULL,
#   level         VARCHAR(16)  NOT NULL,             -- low/medium/high
#   description   TEXT         NULL,
#   created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
#
# DROP TABLE IF EXISTS lg_cleaning_task;
# CREATE TABLE lg_cleaning_task (
#   id            BIGINT PRIMARY KEY AUTO_INCREMENT,
#   area          VARCHAR(128) NOT NULL,
#   duty_time     DATETIME     NOT NULL,
#   staff         VARCHAR(64)  NULL,
#   status        VARCHAR(16)  NOT NULL DEFAULT
#   created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

class Facility(BaseModel):
    """设施表"""
    id = models.AutoField(primary_key=True, verbose_name='设施id')
    name = models.CharField(max_length=128, verbose_name='设施名称', null=False)
    category = models.CharField(max_length=64, verbose_name='设施类别', null=False)
    location = models.CharField(max_length=128, verbose_name='设施位置', null=True)
    status = models.CharField(max_length=32, verbose_name='设施状态', null=False, default='normal')

    class Meta:
        db_table = 'lg_facility'
        verbose_name = '设施表'
        verbose_name_plural = verbose_name


class Maintenance(BaseModel):
    """维修表"""
    id = models.AutoField(primary_key=True, verbose_name='维修id')
    facility_id = models.ForeignKey(Facility, on_delete=models.CASCADE, verbose_name='设施id')
    reporter = models.CharField(max_length=64, verbose_name='报修人', null=True)
    description = models.TextField(verbose_name='维修描述', null=True)
    level = models.CharField(max_length=16, verbose_name='维修等级', null=False, default='medium')
    status = models.CharField(max_length=16, verbose_name='维修状态', null=False, default='open')
    update_time = models.DateTimeField(verbose_name='更新时间', null=False, auto_now=True)

    class Meta:
        db_table = 'lg_maintenance'
        verbose_name = '维修表'
        verbose_name_plural = verbose_name


class CanteenMenu(BaseModel):
    """食堂菜单表"""
    id = models.AutoField(primary_key=True, verbose_name='菜单id')
    canteen = models.CharField(max_length=64, verbose_name='食堂名称', null=False)
    dish_name = models.CharField(max_length=128, verbose_name='菜品名称', null=False)
    price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='菜品价格', null=False)
    tags = models.CharField(max_length=128, verbose_name='菜品标签', null=True)

    class Meta:
        db_table = 'lg_canteen_menu'
        verbose_name = '食堂菜单'
        verbose_name_plural = verbose_name


class SecurityEvent(BaseModel):
    """安全事件表"""
    id = models.AutoField(primary_key=True, verbose_name='事件id')
    title = models.CharField(max_length=128, verbose_name='事件标题', null=False)
    event_time = models.DateTimeField(verbose_name='事件时间', null=False)
    place = models.CharField(max_length=128, verbose_name='事件地点', null=True)
    level = models.CharField(max_length=16, verbose_name='事件等级', null=False)
    description = models.TextField(verbose_name='事件描述', null=True)

    class Meta:
        db_table = 'lg_security_event'
        verbose_name = '安全事件'
        verbose_name_plural = verbose_name


class CleaningTask(BaseModel):
    """清洁任务表"""
    id = models.AutoField(primary_key=True, verbose_name='任务id')
    area = models.CharField(max_length=128, verbose_name='区域名称', null=False)
    duty_time = models.DateTimeField(verbose_name='任务时间', null=False)
    staff = models.CharField(max_length=64, verbose_name='责任人', null=True)
    status = models.CharField(max_length=16, verbose_name='任务状态', null=False, default='todo')

    class Meta:
        db_table = 'lg_cleaning_task'
        verbose_name = '清洁任务'
        verbose_name_plural = verbose_name
