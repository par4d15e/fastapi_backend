from datetime import datetime, timezone
from typing import Any, Mapping, MutableMapping

from sqlalchemy.exc import IntegrityError
from sqlmodel import asc, col, desc, or_, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.users.model import User


class UserRepository:
    """User CRUD"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, user_id: int) -> User | None:
        user = await self.session.get(User, user_id)
        if not user:
            return None

        return user

    async def get_by_username(self, username: str) -> User | None:
        statement = select(User).where(User.username == username)
        result = await self.session.exec(statement)
        user = result.one_or_none()
        if not user:
            return None

        return user

    async def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        result = await self.session.exec(statement)
        user = result.one_or_none()
        if not user:
            return None

        return user

    async def get_all(
        self,
        *,
        search: str | None = None,
        order_by: str = "id",
        direction: str = "asc",
        limit: int = 10,
        offset: int = 0,
    ) -> list[User]:
        query = select(User)

        # 1. 搜索
        if search:
            pattern = f"%{search}%"
            query = query.where(
                or_(col(User.username).ilike(pattern), col(User.email).ilike(pattern))
            )

        # 2. 排序
        allowed_sort = {"id", "username", "created_at"}
        if order_by not in allowed_sort:
            order_by = "id"
        order_column = getattr(User, order_by, User.id)
        query = query.order_by(
            desc(order_column) if direction == "desc" else asc(order_column)
        )

        # 3. 分页
        limit = min(limit, 500)
        offset = max(offset, 0)
        paginated_query = query.offset(offset).limit(limit)
        users = list(await self.session.scalars(paginated_query))

        return users

    async def create(self, user_data: Mapping[str, Any]) -> User:
        hashed_password = get_password_hash(user_data["password"])

        user = User(
            username=user_data["username"],
            email=user_data["email"],
            hashed_password=hashed_password,
            is_verified=False,
        )

        self.session.add(user)
        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise
        await self.session.refresh(user)
        return user

    async def update(
        self, user_id: int, user_data: MutableMapping[str, Any]
    ) -> User | None:
        db_user = await self.get_by_id(user_id)
        if not db_user:
            return None

        if "password" in user_data:
            user_data["hashed_password"] = get_password_hash(user_data.pop("password"))

        for key, value in user_data.items():
            setattr(db_user, key, value)

        db_user.updated_at = datetime.now(timezone.utc)
        await self.session.commit()
        await self.session.refresh(db_user)
        return db_user

    async def delete(self, user_id: int) -> bool:
        db_user = await self.get_by_id(user_id)
        if not db_user:
            return False

        await self.session.delete(db_user)
        await self.session.commit()
        return True

    async def authenticate(self, username: str, password: str) -> User | None:
        user = await self.get_by_username(username)

        if not user:
            user = await self.get_by_email(username)

        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        user.last_login_at = datetime.now(timezone.utc)
        await self.session.commit()
        await self.session.refresh(user)

        return user

    async def verify_email(self, user_id: int) -> User | None:
        db_user = await self.get_by_id(user_id)
        if not db_user:
            return None

        db_user.is_verified = True
        await self.session.commit()
        await self.session.refresh(db_user)
        return db_user

    async def change_password(self, user_id: int, new_password: str) -> User | None:
        db_user = await self.get_by_id(user_id)
        if not db_user:
            return None

        db_user.hashed_password = get_password_hash(new_password)
        db_user.updated_at = datetime.now(timezone.utc)
        await self.session.commit()
        await self.session.refresh(db_user)
        return db_user
