# app/core/exceptions.py
class BusinessError(Exception):
    """业务异常基类，router 层转成 HTTPException"""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code


class NotFoundError(BusinessError):
    def __init__(self, message: str = "资源不存在"):
        super().__init__(message, 404)


class PermissionDeniedError(BusinessError):
    def __init__(self, message: str = "无权限操作"):
        super().__init__(message, 403)


class ConflictError(BusinessError):
    def __init__(self, message: str = "资源冲突"):
        super().__init__(message, 409)