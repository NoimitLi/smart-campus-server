from django.db import models
from Base.Model import BaseModel


# /* ========================= 系统监控 ========================= */
# DROP TABLE IF EXISTS sm_login_log;
# CREATE TABLE sm_login_log (
#   id            BIGINT PRIMARY KEY AUTO_INCREMENT,
#   user_id       VARCHAR(64)  NULL,
#   username      VARCHAR(64)  NULL,
#   ip            VARCHAR(64)  NULL,
#   ua            VARCHAR(256) NULL,
#   status        TINYINT      NOT NULL DEFAULT 1,    -- 1成功0失败
#   message       VARCHAR(255) NULL,
#   login_time    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
#   INDEX idx_user (user_id, username),
#   INDEX idx_time (login_time)
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
#
# DROP TABLE IF EXISTS sm_operation_log;
# CREATE TABLE sm_operation_log (
#   id            BIGINT PRIMARY KEY AUTO_INCREMENT,
#   user_id       VARCHAR(64)  NULL,
#   username      VARCHAR(64)  NULL,
#   module        VARCHAR(64)  NULL,
#   action        VARCHAR(64)  NULL,
#   status        TINYINT      NOT NULL DEFAULT 1,
#   message       VARCHAR(255) NULL,
#   cost_ms       INT          NULL,
#   create_time   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
#   INDEX idx_user (user_id),
#   INDEX idx_module (module),
#   INDEX idx_time (create_time)
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
#
# DROP TABLE IF EXISTS sm_online_user;
# CREATE TABLE sm_online_user (
#   id            BIGINT PRIMARY KEY AUTO_INCREMENT,
#   user_id       VARCHAR(64)  NOT NULL,
#   username      VARCHAR(64)  NOT NULL,
#   token         VARCHAR(256) NOT NULL,
#   ip            VARCHAR(64)  NULL,
#   login_time    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
#   last_active   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
#   INDEX idx_user (user_id),
#   UNIQUE uk_token (token)
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
#
# DROP TABLE IF EXISTS sm_server_metric;
# CREATE TABLE sm_server_metric (
#   id            BIGINT PRIMARY KEY AUTO_INCREMENT,
#   cpu_usage     DECIMAL(5,2) NOT NULL,
#   mem_total_mb  INT          NOT NULL,
#   mem_used_mb   INT          NOT NULL,
#   jvm_usage     DECIMAL(5,2) NULL,
#   os_name       VARCHAR(64)  NULL,
#   os_arch       VARCHAR(64)  NULL,
#   disk_usage    DECIMAL(5,2) NULL,
#   collect_time  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
#   INDEX idx_time (collect_time)
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


class LoginLog(BaseModel):
    """登陆日志表"""
    user_id = models.CharField(max_length=64, null=True, blank=True, verbose_name="用户ID")
    username = models.CharField(max_length=64, null=True, blank=True, verbose_name="用户名")
    ip = models.CharField(max_length=64, null=True, blank=True, verbose_name="IP")
    ua = models.CharField(max_length=256, null=True, blank=True, verbose_name="UA")
    status = models.IntegerField(default=1, verbose_name="状态")
    message = models.CharField(max_length=255, null=True, blank=True, verbose_name="消息")
    login_time = models.DateTimeField(auto_now_add=True, verbose_name="登陆时间")

    class Meta:
        db_table = "sm_login_log"
        verbose_name = "登陆日志表"
        verbose_name_plural = verbose_name


class OperationLog(BaseModel):
    """操作日志表"""
    user_id = models.CharField(max_length=64, null=True, blank=True, verbose_name="用户ID")
    username = models.CharField(max_length=64, null=True, blank=True, verbose_name="用户名")
    module = models.CharField(max_length=64, null=True, blank=True, verbose_name="模块")
    action = models.CharField(max_length=64, null=True, blank=True, verbose_name="动作")
    status = models.IntegerField(default=1, verbose_name="状态")
    message = models.CharField(max_length=255, null=True, blank=True, verbose_name="消息")
    cost_ms = models.IntegerField(null=True, blank=True, verbose_name="耗时")

    class Meta:
        db_table = "sm_operation_log"
        verbose_name = "操作日志表"
        verbose_name_plural = verbose_name


class OnlineUser(BaseModel):
    """在线用户表"""
    user_id = models.CharField(max_length=64, verbose_name="用户ID")
    username = models.CharField(max_length=64, verbose_name="用户名")
    token = models.CharField(max_length=256, verbose_name="Token")
    ip = models.CharField(max_length=64, null=True, blank=True, verbose_name="IP")
    login_time = models.DateTimeField(auto_now_add=True, verbose_name="登陆时间")
    last_active = models.DateTimeField(auto_now=True, verbose_name="最后活跃时间")

    class Meta:
        db_table = "sm_online_user"
        verbose_name = "在线用户表"
        verbose_name_plural = verbose_name


class ServerMetric(BaseModel):
    """服务器指标表"""
    cpu_usage = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="CPU使用率")
    mem_total_mb = models.IntegerField(verbose_name="内存总量(MB)")
    mem_used_mb = models.IntegerField(verbose_name="内存使用量(MB)")
    jvm_usage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="JVM使用率")
    os_name = models.CharField(max_length=64, null=True, blank=True, verbose_name="操作系统名称")
    os_arch = models.CharField(max_length=64, null=True, blank=True, verbose_name="操作系统架构")
    disk_usage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="磁盘使用率")
    collect_time = models.DateTimeField(auto_now_add=True, verbose_name="采集时间")

    class Meta:
        db_table = "sm_server_metric"
        verbose_name = "服务器指标表"
        verbose_name_plural = verbose_name
