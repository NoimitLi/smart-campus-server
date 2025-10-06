from django.db import models
from apps.oauth.models import UserModel
from django.contrib.auth import get_user_model


class ChatRoom(models.Model):
    """
    聊天室模型
    用于表示群聊或私聊的聊天室
    """
    ROOM_TYPES = (
        ('group', '群组聊天'),
        ('private', '私密聊天'),
    )

    # 基础字段
    name = models.CharField('房间名称', max_length=255, unique=True)
    room_type = models.CharField('房间类型', max_length=10, choices=ROOM_TYPES)
    updated_time = models.DateTimeField('更新时间', auto_now=True)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)

    # 关联字段
    members = models.ManyToManyField(
        UserModel,
        related_name='chat_rooms',
        verbose_name='成员列表'
    )

    class Meta:
        verbose_name = '聊天室'
        verbose_name_plural = '聊天室管理'
        indexes = [
            # 为高频查询字段添加索引
            models.Index(fields=['room_type'], name='room_type_idx'),
            # 为高频查询字段添加索引
            models.Index(fields=['created_time'], name='room_created_idx'),
        ]
        ordering = ['-created_time']

    def __str__(self):
        return f"{self.name} ({self.get_room_type_display()})"

    def get_member_count(self):
        """获取聊天室成员数量"""
        return self.members.count()


class ChatMessage(models.Model):
    """
    聊天消息模型
    存储所有聊天消息记录
    """
    # 关联字段
    room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='所属聊天室'
    )
    sender = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name='发送者'
    )

    # 内容字段
    content = models.TextField('消息内容')
    is_read = models.BooleanField('是否已读', default=False)

    # 时间字段
    created_time = models.DateTimeField('发送时间', auto_now_add=True)
    updated_time = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '聊天消息'
        verbose_name_plural = '聊天消息管理'
        indexes = [
            # 复合索引提高查询效率
            models.Index(fields=['room', 'is_read'], name='room_unread_idx'),
            models.Index(fields=['sender', 'is_read'], name='sender_unread_idx'),
            models.Index(fields=['created_time'], name='message_created_idx'),
        ]
        ordering = ['created_time']  # 按时间顺序排序

    def __str__(self):
        return f"{self.sender.username}在{self.room.name}发送的消息"

    def mark_as_read(self):
        """标记消息为已读"""
        self.is_read = True
        self.save()


class UserPresence(models.Model):
    """
    用户在线状态模型
    实时追踪用户在线状态
    """
    user = models.OneToOneField(
        UserModel,
        on_delete=models.CASCADE,
        related_name='presence',
        verbose_name='用户'
    )
    is_online = models.BooleanField('是否在线', default=False)
    last_seen = models.DateTimeField('最后活跃时间', auto_now=True)

    class Meta:
        verbose_name = '用户在线状态'
        verbose_name_plural = '用户在线状态管理'

    def __str__(self):
        return f"{self.user.username} - {'在线' if self.is_online else '离线'}"

    def update_presence(self, online_status):
        """更新用户在线状态"""
        self.is_online = online_status
        self.save()


class Notification(models.Model):
    """
    系统通知模型
    处理所有用户通知
    """
    NOTIFICATION_TYPES = (
        ('message', '新消息'),
        ('friend_request', '好友请求'),
        ('system', '系统通知'),
        ('group_invite', '群组邀请'),
    )

    # 接收者配置
    recipient = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='接收用户'
    )

    # 发送者配置（可选）
    sender = models.ForeignKey(
        UserModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_notifications',
        verbose_name='发送用户'
    )

    # 通知内容
    notification_type = models.CharField(
        '通知类型',
        max_length=20,
        choices=NOTIFICATION_TYPES
    )
    title = models.CharField('通知标题', max_length=255)
    message = models.TextField('通知内容')
    is_read = models.BooleanField('是否已读', default=False)

    # 关联ID（可选，用于关联到具体内容）
    related_id = models.CharField(
        '关联ID',
        max_length=100,
        null=True,
        blank=True,
        help_text='可用于关联消息、群组等'
    )

    # 时间记录
    created_time = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '用户通知'
        verbose_name_plural = '用户通知管理'
        indexes = [
            # 优化未读通知查询
            models.Index(fields=['recipient', 'is_read'], name='unread_notifications_idx'),
            models.Index(fields=['created_time'], name='notification_created_idx'),
        ]
        ordering = ['-created_time']  # 按时间倒序排列

    def __str__(self):
        return f"{self.get_notification_type_display()}通知 - {self.recipient.username}"

    def mark_as_read(self):
        """标记通知为已读"""
        self.is_read = True
        self.save()
        return self
