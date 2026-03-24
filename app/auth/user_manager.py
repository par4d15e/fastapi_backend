import uuid
from typing import Annotated

from loguru import logger
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, UUIDIDMixin
from fastapi_users.db import SQLAlchemyUserDatabase

from app.auth.dependencies import get_user_db
from app.auth.model import User
from app.core.config import settings

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
