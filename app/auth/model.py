from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from fastapi_users_db_sqlalchemy.access_token import SQLAlchemyBaseAccessTokenTableUUID
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base_model import Base, DateTimeMixin

if TYPE_CHECKING:
    pass


class User(SQLAlchemyBaseUserTableUUID, Base, DateTimeMixin):
    __tablename__ = "users"

    # 关系：一个用户可拥有多条食品和多个档案
    foods = relationship("Food", back_populates="user")
    profiles = relationship("Profile", back_populates="user")


class AccessToken(SQLAlchemyBaseAccessTokenTableUUID, Base):
    # 继承自第三方基类，其默认可能引用单数表名 'user'.
    # 显式覆盖 user_id 的外键，确保引用项目中使用的表名 'users'
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
