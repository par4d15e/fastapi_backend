from typing import Annotated

from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users_db_sqlalchemy.access_token import SQLAlchemyAccessTokenDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.model import AccessToken, User
from app.core.database import get_session

""" --- FastAPI Users 专用依赖 --- """


# 获取用户数据库依赖
async def get_user_db(session: Annotated[AsyncSession, Depends(get_session)]):
    yield SQLAlchemyUserDatabase(session, User)


# 获取访问令牌数据库依赖
async def get_access_token_db(session: Annotated[AsyncSession, Depends(get_session)]):
    yield SQLAlchemyAccessTokenDatabase(session, AccessToken)
