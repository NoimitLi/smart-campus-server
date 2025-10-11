from django.db import models
from Base.Model import BaseModel


# /* ========================= 校园服务 ========================= */
# DROP TABLE IF EXISTS cp_library_book;
# CREATE TABLE cp_library_book (
#   id            BIGINT PRIMARY KEY AUTO_INCREMENT,
#   isbn          VARCHAR(32)  NOT NULL,
#   title         VARCHAR(256) NOT NULL,
#   author        VARCHAR(128) NULL,
#   publisher     VARCHAR(128) NULL,
#   publish_date  DATE         NULL,
#   stock         INT          NOT NULL DEFAULT 0,
#   created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
#   UNIQUE uk_isbn (isbn)
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
#
# DROP TABLE IF EXISTS cp_sport_place;
# CREATE TABLE cp_sport_place (
#   id            BIGINT PRIMARY KEY AUTO_INCREMENT,
#   name          VARCHAR(128) NOT NULL,             -- 场所名称
#   type          VARCHAR(64)  NOT NULL,             -- 篮球/羽毛球/游泳
#   open_time     VARCHAR(64)  NULL,
#   status        VARCHAR(16)  NOT NULL DEFAULT 'open', -- open/close
#   created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
#
# DROP TABLE IF EXISTS cp_transport_line;
# CREATE TABLE cp_transport_line (
#   id            BIGINT PRIMARY KEY AUTO_INCREMENT,
#   line_name     VARCHAR(128) NOT NULL,             -- 校园巴士线路
#   start_point   VARCHAR(128) NOT NULL,
#   end_point     VARCHAR(128) NOT NULL,
#   first_time    TIME         NULL,
#   last_time     TIME         NULL,
#   interval_min  INT          NULL,
#   created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
#
# DROP TABLE IF EXISTS cp_wifi_hotspot;
# CREATE TABLE cp_wifi_hotspot (
#   id            BIGINT PRIMARY KEY AUTO_INCREMENT,
#   ssid          VARCHAR(128) NOT NULL,
#   building      VARCHAR(128) NULL,
#   floor         VARCHAR(32)  NULL,
#   status        VARCHAR(16)  NOT NULL DEFAULT 'online', -- online/offline
#   created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
#
# DROP TABLE IF EXISTS cp_notification;
# CREATE TABLE cp_notification (
#   id            BIGINT PRIMARY KEY AUTO_INCREMENT,
#   title         VARCHAR(256) NOT NULL,
#   content       TEXT         NOT NULL,
#   publisher     VARCHAR(64)  NULL,
#   publish_time  DATETIME     NOT NULL,
#   type          VARCHAR(32)  NULL,                 -- 校务/讲座/活动
#   created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
#

class LibraryBook(BaseModel):
    """图书表"""
    id = models.AutoField(primary_key=True, verbose_name='图书id')
    isbn = models.CharField(max_length=32, verbose_name='ISBN', unique=True)
    title = models.CharField(max_length=256, verbose_name='书名')
    author = models.CharField(max_length=128, verbose_name='作者', null=True, blank=True)
    publisher = models.CharField(max_length=128, verbose_name='出版社', null=True, blank=True)
    publish_date = models.DateField(verbose_name='出版日期', null=True, blank=True)
    stock = models.IntegerField(verbose_name='库存', default=0)

    class Meta:
        db_table = 'cp_library_book'
        verbose_name = '图书'
        verbose_name_plural = verbose_name


class SportPlace(BaseModel):
    """运动场所表"""
    id = models.AutoField(primary_key=True, verbose_name='场所id')
    name = models.CharField(max_length=128, verbose_name='场所名称')
    type = models.CharField(max_length=64, verbose_name='运动类型')
    open_time = models.CharField(max_length=64, verbose_name='开放时间', null=True, blank=True)
    status = models.CharField(max_length=16, verbose_name='状态', default='open')

    class Meta:
        db_table = 'cp_sport_place'
        verbose_name = '运动场所'
        verbose_name_plural = verbose_name


class TransportLine(BaseModel):
    """校园巴士线路表"""
    id = models.AutoField(primary_key=True, verbose_name='线路id')
    line_name = models.CharField(max_length=128, verbose_name='线路名称')
    start_point = models.CharField(max_length=128, verbose_name='起点')
    end_point = models.CharField(max_length=128, verbose_name='终点')
    first_time = models.TimeField(verbose_name='首班车时间', null=True, blank=True)
    last_time = models.TimeField(verbose_name='末班车时间', null=True, blank=True)
    interval_min = models.IntegerField(verbose_name='发车间隔（分钟）', null=True, blank=True)

    class Meta:
        db_table = 'cp_transport_line'
        verbose_name = '校园巴士线路'
        verbose_name_plural = verbose_name


class WifiHotspot(BaseModel):
    """WiFi热点表"""
    id = models.AutoField(primary_key=True, verbose_name='热点id')
    ssid = models.CharField(max_length=128, verbose_name='SSID')
    building = models.CharField(max_length=128, verbose_name='所在楼栋', null=True, blank=True)
    floor = models.CharField(max_length=32, verbose_name='所在楼层', null=True, blank=True)
    status = models.CharField(max_length=16, verbose_name='状态', default='online')

    class Meta:
        db_table = 'cp_wifi_hotspot'
        verbose_name = 'WiFi热点'
        verbose_name_plural = verbose_name


class Notification(BaseModel):
    """通知表"""
    id = models.AutoField(primary_key=True, verbose_name='通知id')
    title = models.CharField(max_length=256, verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    publisher = models.CharField(max_length=64, verbose_name='发布者', null=True, blank=True)
    publish_time = models.DateTimeField(verbose_name='发布时间')
    type = models.CharField(max_length=32, verbose_name='类型', null=True, blank=True)

    class Meta:
        db_table = 'cp_notification'
        verbose_name = '通知'
        verbose_name_plural = verbose_name
