import json
import logging
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from utils.token import verify_token
from ..models import Notification, ChatMessage, UserPresence

logger = logging.getLogger(__name__)


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    """处理所有通知相关的WebSocket通信"""

    async def connect(self):
        """处理WebSocket连接"""
        try:
            # 从查询参数获取token
            query_params = self.get_query_params()
            token = query_params.get('token')

            if not token:
                await self.close(code=4001)
                return

            # 验证token
            payload = verify_token(token)
            if not payload:
                await self.close(code=4001)
                return

            # 设置用户属性
            self.user_id = str(payload['user_id'])
            self.group_name = f"notifications_{self.user_id}"

            # 加入个人通知组
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )

            # 更新在线状态
            await self.set_user_online(True)

            # 接受连接
            await self.accept()

            # 发送连接确认
            await self.send_json({
                "type": "connection_established",
                "message": "连接成功",
                "user_id": self.user_id,
                "timestamp": timezone.now().isoformat()
            })

            # 发送待处理通知
            await self.send_pending_notifications()

        except Exception as e:
            logger.error(f"连接错误: {str(e)}", exc_info=True)
            await self.close(code=4000)

    async def disconnect(self, close_code):
        """处理断开连接"""
        try:
            if hasattr(self, 'group_name'):
                await self.channel_layer.group_discard(
                    self.group_name,
                    self.channel_name
                )

            if hasattr(self, 'user_id'):
                await self.set_user_online(False)

        except Exception as e:
            logger.error(f"断开连接错误: {str(e)}", exc_info=True)

    async def receive_json(self, content, **kwargs):
        """处理收到的JSON消息"""
        try:
            message_type = content.get('type')

            if message_type == 'init':
                # 初始化处理
                await self.handle_init(content)
            elif message_type == 'command':
                # 命令处理
                await self.handle_command(content)
            elif message_type == 'read_notification':
                # 已读回执
                await self.handle_read_notification(content)
            else:
                await self.send_error("未知消息类型", code="unknown_type")

        except json.JSONDecodeError:
            await self.send_error("无效的JSON格式", code="invalid_json")
        except KeyError as e:
            await self.send_error(f"缺少必要字段: {str(e)}", code="missing_field")
        except Exception as e:
            logger.error(f"消息处理错误: {str(e)}", exc_info=True)
            await self.send_error("内部服务器错误", code="server_error")

    async def handle_init(self, content):
        """处理初始化消息"""
        client_user_id = content.get('data', {}).get('userId')
        if str(client_user_id) != self.user_id:
            await self.send_error("用户ID不匹配", code="user_mismatch")
            return

        await self.send_json({
            "type": "init_success",
            "message": "初始化成功",
            "timestamp": timezone.now().isoformat()
        })

    async def handle_command(self, content):
        """处理命令请求"""
        command = content.get('data', {}).get('command')
        data = content.get('data', {}).get('data', {})

        if command == 'get_message_list':
            messages = await self.get_recent_messages()
            await self.send_json({
                "type": "command",
                "data": {
                    "command": "message_list_result",
                    "data": messages
                },
                "timestamp": timezone.now().isoformat()
            })
        elif command == 'get_notification_list':
            notifications = await self.get_recent_notifications()
            await self.send_json({
                "type": "command",
                "data": {
                    "command": "notification_list_result",
                    "data": notifications
                },
                "timestamp": timezone.now().isoformat()
            })
        else:
            await self.send_error(f"未知命令: {command}", code="unknown_command")

    async def handle_read_notification(self, content):
        """处理通知已读回执"""
        notification_id = content.get('data', {}).get('notification_id')
        if not notification_id:
            await self.send_error("缺少通知ID", code="missing_id")
            return

        success = await self.mark_notification_read(notification_id)
        await self.send_json({
            "type": "command",
            "data": {
                "command": "read_notification_result",
                "success": success,
                "id": notification_id
            },
            "timestamp": timezone.now().isoformat()
        })

    async def send_pending_notifications(self):
        """发送待处理通知"""
        notifications = await self.get_unread_notifications()
        if notifications:
            await self.send_json({
                "type": "notification",
                "data": {
                    "command": "new_notification",
                    "data": notifications
                },
                "timestamp": timezone.now().isoformat()
            })

    async def send_notification(self, event):
        """发送通知给客户端"""
        await self.send_json({
            "type": "notification",
            "data": event["data"],
            "timestamp": timezone.now().isoformat()
        })

    async def send_command(self, event):
        """发送命令给客户端"""
        await self.send_json({
            "type": "command",
            "data": event["data"],
            "timestamp": timezone.now().isoformat()
        })

    async def send_error(self, message, code=None):
        """发送错误消息"""
        error_data = {
            "type": "error",
            "message": message,
            "timestamp": timezone.now().isoformat()
        }
        if code:
            error_data["code"] = code
        await self.send_json(error_data)

    def get_query_params(self):
        """从查询字符串获取参数"""
        query_string = self.scope.get('query_string', b'').decode()
        return dict(p.split('=') for p in query_string.split('&') if '=' in p)

    @database_sync_to_async
    def set_user_online(self, is_online):
        """更新用户在线状态"""
        UserPresence.objects.update_or_create(
            user_id=self.user_id,
            defaults={
                'is_online': is_online,
                'last_seen': timezone.now()
            }
        )

    @database_sync_to_async
    def get_unread_notifications(self):
        """获取未读通知"""
        return list(Notification.objects.filter(
            recipient_id=self.user_id,
            is_read=False
        ).order_by('-created_time').values(
            'id', 'notification_type', 'title', 'message', 'created_time'
        )[:50])  # 限制最多50条

    @database_sync_to_async
    def get_recent_messages(self):
        """获取最近消息"""
        return list(ChatMessage.objects.filter(
            room__members=self.user_id
        ).order_by('-created_time').select_related('sender', 'room').values(
            'id', 'content', 'is_read', 'created_time',
            'sender__username', 'room__name'
        )[:50])  # 限制最多50条

    @database_sync_to_async
    def get_recent_notifications(self):
        """获取最近通知"""
        return list(Notification.objects.filter(
            recipient_id=self.user_id
        ).order_by('-created_time').values(
            'id', 'notification_type', 'title', 'message',
            'is_read', 'created_time'
        )[:50])  # 限制最多50条

    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        """标记通知为已读"""
        updated = Notification.objects.filter(
            id=notification_id,
            recipient_id=self.user_id
        ).update(is_read=True)
        return updated > 0
