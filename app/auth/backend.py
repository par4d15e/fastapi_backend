import uuid
from typing import Annotated

from fastapi import Depends
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    CookieTransport,
)
from fastapi_users.authentication.strategy.db import (
    AccessTokenDatabase,
    DatabaseStrategy,
)

from app.auth.dependencies import get_access_token_db
from app.auth.model import AccessToken, User
from app.auth.user_manager import get_user_manager
from app.core.config import settings

# token 传输方式
bearer_transport = BearerTransport(tokenUrl="auth/token/login")

# Cookie 安全配置：生产环境要开启 HTTPS、HttpOnly、Strict 同站策略
cookie_transport = CookieTransport(
    cookie_max_age=3600,
    cookie_secure=not settings.debug,
    cookie_httponly=True,
    cookie_samesite="strict",
)


# 数据库策略（依赖 users.dependencies 的 get_access_token_db）
def get_database_strategy(
    access_token_db: Annotated[
        AccessTokenDatabase[AccessToken], Depends(get_access_token_db)
    ],
) -> DatabaseStrategy:
    return DatabaseStrategy(access_token_db, lifetime_seconds=3600)


# # redis策略
# def get_redis_strategy(auth_redis: Redis = Depends(get_auth_redis)) -> RedisStrategy:
#     return RedisStrategy(auth_redis, lifetime_seconds=3600)


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

# # Redis 认证后端
# redis_auth_backend = AuthenticationBackend(
#     name="Redis Strategy",
#     transport=bearer_transport,
#     get_strategy=get_redis_strategy,
# )

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [cookie_database_auth_backend, bearer_database_auth_backend],
)
