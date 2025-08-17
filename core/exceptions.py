class APIError(Exception):
    """基础API异常"""

    def __init__(self, message, code=400):
        self.code = code
        self.message = message


class AuthFailed(APIError):
    """认证失败异常"""

    def __init__(self, message='认证失败'):
        super().__init__(message, code=401)


class TokenInvalid(APIError):
    """Token无效异常"""

    def __init__(self, message='Token无效'):
        super().__init__(message, code=401)
