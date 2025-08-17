import jwt
from datetime import datetime, timedelta
from .generate import generate_random_str
from typing import Optional

SECRET_KEY = 'jwt-secret-key'
EXPIRE_TIME = 3600  # 默认过期时间


def generate_token(data: dict, expire=EXPIRE_TIME) -> str:
    """生成token"""
    if isinstance(expire, timedelta):
        expire = expire.seconds
    exp = datetime.now() + timedelta(seconds=expire)

    payload = {
        'data': data,
        'exp': exp,
        # 'signature': generate_random_str(32)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token


def decode_token(token: str) -> dict:
    """解析token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload['data']
    except jwt.ExpiredSignatureError:
        raise Exception('Token已过期')
    except jwt.InvalidTokenError:
        raise Exception('无效的Token')


def format_token(token: str) -> str:
    """格式化token"""
    if token.startswith('Bearer '):
        return token
    return f'Bearer {token}'


def parsing_token(token: str) -> str:
    """解析token"""
    if not token.startswith('Bearer '):
        return token
    return token[7:]


def verify_token(token) -> Optional[dict]:
    token = parsing_token(token)
    try:
        payload = decode_token(token)
        return payload
    except:
        return None
