# src/auth/router.py
from fastapi import FastAPI
from fastapi_users import FastAPIUsers

from app.auth.schema import UserCreate, UserRead, UserUpdate
from app.auth.user_manager import (
    bearer_database_auth_backend,
    cookie_database_auth_backend,
)


def register_fastapi_users_routes(
    app: FastAPI,
    fastapi_users: FastAPIUsers,
) -> None:
    """把 FastAPI-Users 的所有 router 挂到 app 上"""

    # 生成 Bearer 登录路由
    app.include_router(
        fastapi_users.get_auth_router(bearer_database_auth_backend),
        prefix="/auth/token",
        tags=["auth"],
    )

    # 生成 Cookie 登录路由
    app.include_router(
        fastapi_users.get_auth_router(cookie_database_auth_backend),
        prefix="/auth/cookie",
        tags=["auth"],
    )

    # 生成注册路由 /auth/register
    app.include_router(
        fastapi_users.get_register_router(UserRead, UserCreate),
        prefix="/auth",
        tags=["auth"],
    )

    # 生成重置密码路由 /auth/reset-password
    app.include_router(
        fastapi_users.get_reset_password_router(),
        prefix="/auth",
        tags=["auth"],
    )

    # 生成验证邮箱路由 /auth/verify
    app.include_router(
        fastapi_users.get_verify_router(UserRead),
        prefix="/auth",
        tags=["auth"],
    )

    # 生成用户管理路由 /users/me, /users/{id} 等
    app.include_router(
        fastapi_users.get_users_router(UserRead, UserUpdate),
        prefix="/users",
        tags=["users"],
    )
