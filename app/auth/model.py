from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from fastapi_users_db_sqlalchemy.access_token import SQLAlchemyBaseAccessTokenTableUUID
from sqlalchemy.orm import relationship

from app.core.base_model import Base, DateTimeMixin

if TYPE_CHECKING:
    pass


class User(SQLAlchemyBaseUserTableUUID, Base, DateTimeMixin):
    # 关系：一个用户可拥有多条食品和多个档案
    foods = relationship("Food", back_populates="user")
    profiles = relationship("Profile", back_populates="user")


class AccessToken(SQLAlchemyBaseAccessTokenTableUUID, Base):
    pass
