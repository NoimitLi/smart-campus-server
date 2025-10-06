import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.utils import timezone

logger = logging.getLogger(__name__)
User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    """
    聊天WebSocket消费者
    处理所有实时聊天功能，包括：
    - 群组聊天
    - 私密聊天
    - 消息已读回执
    - 输入状态指示
    """

    async def connect(self):
        """
        处理WebSocket连接
        流程：
        1. 验证用户认证
        2. 检查房间访问权限
        3. 加入房间组
        4. 发送加入通知
        """
        try:
            # 1. 获取并验证用户
            self.user = self.scope["user"]
            if not self.user.is_authenticated:
                await self.close(code=4003)  # 未认证错误代码
                return

            # 2. 获取房间信息
            self.room_name = self.scope['url_route']['kwargs']['room_name']
            self.room_group_name = f"chat_{self.room_name}"

            # 3. 验证房间访问权限
            if not await self.verify_room_access(self.user.id, self.room_name):
                await self.close(code=4004)  # 无权限错误代码
                return

            # 4. 加入房间组
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()

            # 5. 发送加入通知
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "system_message",
                    "message": f"{self.user.username} 加入了聊天",
                    "username": "系统通知"
                }
            )

            logger.info(f"用户 {self.user.username} 加入了房间 {self.room_name}")

        except Exception as e:
            logger.error(f"连接错误: {str(e)}", exc_info=True)
            await self.close(code=4000)  # 通用错误代码

    async def disconnect(self, close_code):
        """
        处理WebSocket断开连接
        流程：
        1. 发送离开通知
        2. 从房间组移除
        """
        try:
            if hasattr(self, 'room_group_name'):
                # 1. 发送离开通知
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "system_message",
                        "message": f"{self.user.username} 离开了聊天",
                        "username": "系统通知"
                    }
                )

                # 2. 从组中移除
                await self.channel_layer.group_discard(
                    self.room_group_name,
                    self.channel_name
                )

                logger.info(f"用户 {self.user.username} 离开了房间 {self.room_name}")

        except Exception as e:
            logger.error(f"断开连接错误: {str(e)}", exc_info=True)

    async def receive(self, text_data):
        """
        处理客户端发送的消息
        支持的消息类型：
        - chat_message: 聊天消息
        - read_receipt: 已读回执
        - typing: 输入状态
        """
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'chat_message':
                await self.handle_chat_message(data)
            elif message_type == 'read_receipt':
                await self.handle_read_receipt(data)
            elif message_type == 'typing':
                await self.handle_typing_indicator(data)
            else:
                logger.warning(f"未知消息类型: {message_type}")
                await self.send_error("不支持的消息类型", code="unsupported_type")

        except json.JSONDecodeError:
            await self.send_error("无效的JSON格式", code="invalid_json")
        except KeyError as e:
            await self.send_error(f"缺少必要字段: {str(e)}", code="missing_field")
        except Exception as e:
            logger.error(f"消息处理错误: {str(e)}", exc_info=True)
            await self.send_error("内部服务器错误", code="server_error")

    async def handle_chat_message(self, data):
        """
        处理聊天消息
        支持的消息类型：
        - group: 群组消息
        - private: 私聊消息
        """
        message = data.get('message')
        message_type = data.get('message_type', 'group')  # 默认为群组消息

        # 验证消息内容
        if not message:
            await self.send_error("消息内容不能为空", code="empty_message")
            return

        try:
            # 保存消息到数据库
            message_id = await self.save_message(
                self.user.id,
                self.room_name,
                message,
                message_type
            )

            # 准备消息数据
            message_data = {
                "id": message_id,
                "user_id": str(self.user.id),
                "username": self.user.username,
                "avatar": await self.get_user_avatar(self.user.id),
                "message": message,
                "timestamp": timezone.now().isoformat(),
                "type": message_type,
                "room_name": self.room_name
            }

            # 特殊处理私聊消息
            if message_type == 'private':
                await self.handle_private_message(data, message_data)
            else:
                # 广播群组消息
                await self.broadcast_message(message_data)

        except Exception as e:
            logger.error(f"消息处理错误: {str(e)}", exc_info=True)
            await self.send_error("消息发送失败", code="message_failed")

    async def handle_private_message(self, data, message_data):
        """
        处理私聊消息
        特殊流程：
        1. 验证私聊关系
        2. 单独发送给接收者
        3. 发送回执给发送者
        """
        recipient_id = data.get('recipient_id')
        if not recipient_id:
            await self.send_error("缺少接收者ID", code="missing_recipient")
            return

        # 验证私聊关系
        if not await self.verify_private_chat(self.user.id, recipient_id, self.room_name):
            await self.send_error("无效的私聊会话", code="invalid_private_chat")
            return

        # 添加私聊标记
        message_data.update({
            'is_private': True,
            'recipient_id': recipient_id
        })

        # 发送给接收者的通知通道
        recipient_group = f"notifications_{recipient_id}"
        await self.channel_layer.group_send(
            recipient_group,
            {
                "type": "private_message",
                "data": message_data
            }
        )

        # 发送回执给发送者
        await self.send(text_data=json.dumps({
            "type": "chat_message",
            "data": {**message_data, "is_self": True}
        }))

    async def handle_read_receipt(self, data):
        """
        处理消息已读回执
        流程：
        1. 标记消息为已读
        2. 可选通知发送者
        """
        message_id = data.get('message_id')
        if not message_id:
            await self.send_error("缺少消息ID", code="missing_message_id")
            return

        # 标记消息为已读
        await self.mark_message_read(message_id, self.user.id)

        # 如果需要通知发送者
        if data.get('notify_sender'):
            sender_id = await self.get_message_sender(message_id)
            if sender_id:
                await self.channel_layer.group_send(
                    f"notifications_{sender_id}",
                    {
                        "type": "read_receipt",
                        "message_id": message_id,
                        "reader_id": str(self.user.id),
                        "room_name": self.room_name,
                        "timestamp": timezone.now().isoformat()
                    }
                )

    async def handle_typing_indicator(self, data):
        """
        处理用户输入状态
        广播给房间内其他用户
        """
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "typing_indicator",
                "user_id": str(self.user.id),
                "username": self.user.username,
                "is_typing": data.get('is_typing', False),
                "room_name": self.room_name
            }
        )

    # ========== 消息类型处理方法 ==========

    async def chat_message(self, event):
        """发送聊天消息给客户端"""
        await self.send(text_data=json.dumps({
            "type": "chat_message",
            "data": event["data"]
        }))

    async def system_message(self, event):
        """发送系统消息给客户端"""
        await self.send(text_data=json.dumps({
            "type": "system_message",
            "message": event["message"],
            "username": event["username"],
            "timestamp": timezone.now().isoformat()
        }))

    async def typing_indicator(self, event):
        """发送输入状态指示给客户端"""
        await self.send(text_data=json.dumps({
            "type": "typing",
            "user_id": event["user_id"],
            "username": event["username"],
            "is_typing": event["is_typing"],
            "room_name": event["room_name"]
        }))

    async def private_message(self, event):
        """发送私聊消息给客户端"""
        await self.send(text_data=json.dumps({
            "type": "private_message",
            "data": event["data"]
        }))

    async def send_error(self, message, code=None):
        """发送错误消息给客户端"""
        error_data = {
            "type": "error",
            "message": message,
            "timestamp": timezone.now().isoformat()
        }
        if code:
            error_data["code"] = code

        await self.send(text_data=json.dumps(error_data))

    # ========== 数据库操作方法 ==========

    @database_sync_to_async
    def verify_room_access(self, user_id, room_name):
        """验证用户是否有权限访问房间"""
        from ..models import ChatRoom
        return ChatRoom.objects.filter(
            name=room_name,
            members__id=user_id
        ).exists()

    @database_sync_to_async
    def verify_private_chat(self, user1_id, user2_id, room_name):
        """验证是否为有效的私聊会话"""
        from ..models import ChatRoom
        return ChatRoom.objects.filter(
            name=room_name,
            room_type='private',
            members__id__in=[user1_id, user2_id]
        ).distinct().count() == 1

    @database_sync_to_async
    def save_message(self, user_id, room_name, content, message_type):
        """保存消息到数据库"""
        from ..models import ChatMessage, ChatRoom
        room = ChatRoom.objects.get(name=room_name)
        message = ChatMessage.objects.create(
            room=room,
            sender_id=user_id,
            content=content,
            message_type=message_type
        )
        return str(message.id)

    @database_sync_to_async
    def mark_message_read(self, message_id, user_id):
        """标记消息为已读"""
        from ..models import ChatMessage
        updated = ChatMessage.objects.filter(
            id=message_id,
            room__members=user_id
        ).update(is_read=True)
        return updated > 0

    @database_sync_to_async
    def get_message_sender(self, message_id):
        """获取消息发送者ID"""
        from ..models import ChatMessage
        message = ChatMessage.objects.filter(id=message_id).first()
        return str(message.sender_id) if message else None

    @database_sync_to_async
    def get_user_avatar(self, user_id):
        """获取用户头像URL"""
        user = User.objects.filter(id=user_id).first()
        return user.avatar.url if user and hasattr(user, 'avatar') else ""
