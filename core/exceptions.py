class APIError(Exception):
    """基础API异常"""

    def __init__(self, message, code=400):
        self.code = code
        self.message = message


class AuthFailed(APIError):
    """认证失败异常"""

    def __init__(self, message='认证失败'):
        super().__init__(message, code=401)
