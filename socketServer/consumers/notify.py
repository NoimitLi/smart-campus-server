from channels.generic.websocket import AsyncWebsocketConsumer
import json
from utils.token import verify_token


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # 从查询参数获取token
        query_params = dict(p.split('=') for p in self.scope['query_string'].decode().split('&') if p)
        token = query_params.get('token')
        if not token:
            await self.close(code=4001)
            return
        # 验证token
        payload = verify_token(token)
        if not payload:
            await self.close(code=4001)
            return
        else:
            self.group_name = f"notifications_{payload['user_id']}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
            await self.send(text_data=json.dumps({"message": "Connected to notification channel"}))

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        # 处理客户端消息
        await self.send(text_data=json.dumps({
            "type": "echo",
            "message": data
        }))

    async def send_notification(self, event):
        """从组发送通知"""
        await self.send(text_data=json.dumps(event["message"]))
