# import datetime
# from django.http.response import HttpResponse
#
# # 认证Cookie配置
# AUTH_COOKIE_NAME = 'app_auth_token'  # 避免使用常见名称如'sessionid'
# AUTH_COOKIE_PATH = '/api/'  # 限制Cookie只对API路径有效
# AUTH_COOKIE_DOMAIN = '.yourdomain.com'  # 生产环境设置
# AUTH_COOKIE_HTTPONLY = True  # 防止XSS
# AUTH_COOKIE_SECURE = not DEBUG  # 调试时不强制HTTPS
# AUTH_COOKIE_SAMESITE = 'Lax'  # 安全平衡策略
# AUTH_COOKIE_AGE = 30 * 24 * 3600  # 30天（记住我功能）
#
#
# def set_auth_cookie(response, token, remember_me=False):
#     """设置认证Cookie的安全方法"""
#     # 根据是否"记住我"设置不同有效期
#     if remember_me:
#         max_age = settings.SESSION_COOKIE_AGE  # 通常30天
#         expires = datetime.now() + timedelta(seconds=max_age)
#     else:
#         max_age = None  # 会话Cookie（浏览器关闭失效）
#         expires = None
#
#     response.set_cookie(
#         key=settings.AUTH_COOKIE_NAME,  # 例如: 'auth_token'
#         value=token,
#         max_age=max_age,
#         expires=expires,
#         path=settings.AUTH_COOKIE_PATH or '/',
#         domain=settings.AUTH_COOKIE_DOMAIN,
#         secure=settings.SESSION_COOKIE_SECURE or not settings.DEBUG,
#         httponly=True,
#         samesite='Lax'
#     )
