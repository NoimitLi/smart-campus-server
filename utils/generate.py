import random

ACCOUNT_PREV = 'sc-'


def generate_random_str(length: int = 16, mixin: bool = True) -> str:
    """
    生成随机字符串

    :param length: 字符串长度，默认16
    :param mixin: 是否包含字母，默认True(包含)
    :return: 随机字符串
    """
    key = '1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ' if mixin else '1234567890'
    return ''.join(random.choices(key, k=length))


def generate_random_account():
    return ACCOUNT_PREV + generate_random_str()
