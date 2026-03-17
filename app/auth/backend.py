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

from app.users.dependencies import get_access_token_db
from app.users.model import AccessToken
from app.users.model import User
from app.users.user_manager import get_user_manager

# cookie 传输方式
cookie_transport = CookieTransport(cookie_max_age=3600)

# bearer 传输方式
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


# 数据库策略（依赖 users 的 access token db）
def get_database_strategy(
    access_token_db: Annotated[
        AccessTokenDatabase[AccessToken], Depends(get_access_token_db)
    ],
) -> DatabaseStrategy:
    return DatabaseStrategy(access_token_db, lifetime_seconds=3600)

# # redis策略
# def get_redis_strategy(auth_redis: Redis = Depends(get_auth_redis)) -> RedisStrategy:
#     return RedisStrategy(auth_redis, lifetime_seconds=3600)


# 数据库认证后端
database_auth_backend = AuthenticationBackend(
    name="Database Strategy",
    transport=cookie_transport,
    get_strategy=get_database_strategy,
)

# # Redis 认证后端
# redis_auth_backend = AuthenticationBackend(
#     name="Redis Strategy",
#     transport=bearer_transport,
#     get_strategy=get_redis_strategy,
# )


fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager, [database_auth_backend]
)