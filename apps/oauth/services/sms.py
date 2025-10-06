from django.core.cache import cache
import random
import logging

logger = logging.getLogger(__name__)


class SmsService:
    def __init__(self):
        self.cache_prefix = "sms-code:"

    def send_sms_code(self, phone: str) -> bool:
        """发送短信验证码（模拟实现）"""
        code = self._generate_code()
        if self.save_sms_code(phone, code):
            print(code)
            logger.info(f"模拟发送短信验证码：{phone} -> {code}")
            return True
        return False

    def verify_sms_code(self, phone: str, code: str) -> bool:
        """验证短信验证码"""
        cached_code = cache.get(f"{self.cache_prefix}{phone}")
        return cached_code == code

    def save_sms_code(self, phone: str, code: str, expire: int = 300) -> bool:
        """存储验证码（5分钟有效期）"""
        try:
            cache.set(f"{self.cache_prefix}{phone}", code, timeout=expire)
            return True
        except Exception as e:
            logger.error(f"存储验证码失败：{str(e)}")
            return False

    @staticmethod
    def _generate_code(length: int = 6) -> str:
        """生成数字验证码"""
        return ''.join(str(random.randint(0, 9)) for _ in range(length))