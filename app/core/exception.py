# app/core/exceptions.py
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from loguru import logger


# ------------------ 业务异常 ------------------
class NotFoundException(HTTPException):
    def __init__(self, detail: str = "Resource not found"):
        """初始化NotFoundException。"""
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class AlreadyExistsException(HTTPException):
    def __init__(self, detail: str = "Resource already exists"):
        """初始化AlreadyExistsException。"""
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class UnauthorizedException(HTTPException):
    def __init__(self, detail: str = "Unauthorized access"):
        """初始化UnauthorizedException。"""
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class ForbiddenException(HTTPException):
    def __init__(self, detail: str = "Access forbidden"):
        """初始化ForbiddenException。"""
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


# ------------------ 全局兜底 ------------------
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """将异常转换为统一的 HTTP 响应。"""
    logger.exception(f"Unhandled exception at {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


# 专门用于注册全局异常的函数
def register_exception_handlers(app: FastAPI) -> None:
    """注册全局异常处理器。"""
    app.add_exception_handler(Exception, global_exception_handler)
