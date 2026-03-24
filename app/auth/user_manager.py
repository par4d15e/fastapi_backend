import uuid
from typing import Annotated

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    CookieTransport,
)
from fastapi_users.authentication.strategy.db import (
    AccessTokenDatabase,
    DatabaseStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase
from loguru import logger

from app.auth.dependencies import get_access_token_db, get_user_db
from app.auth.model import AccessToken, User
from app.core.config import settings

# ------------------------ 用户管理器 -----------------------

SECRET = settings.jwt_secret


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Request | None = None):
        logger.info("User registered", user_id=user.id, email=user.email)

    async def on_after_forgot_password(
        self, user: User, token: str, request: Request | None = None
    ):
        logger.info(
            "Password reset requested",
            user_id=user.id,
            email=user.email,
            reset_token=token,
        )

    async def on_after_request_verify(
        self, user: User, token: str, request: Request | None = None
    ):
        logger.info(
            "Verification email requested",
            user_id=user.id,
            email=user.email,
            verification_token=token,
        )

    async def on_after_login(
        self,
        user: User,
        request: Request | None = None,
        response=None,
    ):
        logger.info("User login success", user_id=user.id, email=user.email)

    async def on_after_login_failed(
        self,
        request: Request | None = None,
        reason: str | None = None,
    ):
        logger.warning(
            "User login failed",
            details=reason or "unknown reason",
            path=request.url.path if request else None,
        )


async def get_user_manager(
    user_db: Annotated[SQLAlchemyUserDatabase, Depends(get_user_db)],
):
    yield UserManager(user_db)


# ----------------------- 认证后端 -----------------------

# token 传输方式
bearer_transport = BearerTransport(tokenUrl="auth/token/login")

# Cookie 安全配置：生产环境要开启 HTTPS、HttpOnly、Strict 同站策略
cookie_transport = CookieTransport(
    cookie_max_age=3600,
    cookie_secure=not settings.debug,
    cookie_httponly=True,
    cookie_samesite="strict",
)


# 数据库策略（依赖 auth.dependencies 的 get_access_token_db）
def get_database_strategy(
    access_token_db: Annotated[
        AccessTokenDatabase[AccessToken], Depends(get_access_token_db)
    ],
) -> DatabaseStrategy:
    return DatabaseStrategy(access_token_db, lifetime_seconds=3600)


# 数据库认证后端（Bearer）
bearer_database_auth_backend = AuthenticationBackend(
    name="Database Strategy Bearer",
    transport=bearer_transport,  # 使用 Bearer 传输方式
    get_strategy=get_database_strategy,
)

# 数据库认证后端（Cookie）
cookie_database_auth_backend = AuthenticationBackend(
    name="Database Strategy Cookie",
    transport=cookie_transport,  # 使用 Cookie 传输方式
    get_strategy=get_database_strategy,
)


fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [cookie_database_auth_backend, bearer_database_auth_backend],
)
