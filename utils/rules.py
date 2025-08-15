import re


def phone_validator(phone: str) -> bool:
    """手机号验证"""
    reg = r'^1[3-9]\d{9}$'
    if re.match(reg, phone):
        return True
    return False
