from sqlalchemy.exc import IntegrityError

from app.core.exception import AlreadyExistsException, NotFoundException
from app.users.repository import UserRepository
from app.users.schema import UserCreate, UserResponse, UserUpdate


class UserService:
    """User 服务层：封装业务逻辑并调用 repository"""

    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    async def get_user_by_username(self, username: str) -> UserResponse:
        user = await self.repository.get_by_username(username)
        if not user:
            raise NotFoundException("User not found")

        return UserResponse.model_validate(user)

    async def get_user_by_id(self, user_id: int) -> UserResponse:
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")

        return UserResponse.model_validate(user)

    async def get_user_by_email(self, email: str) -> UserResponse:
        user = await self.repository.get_by_email(email)
        if not user:
            raise NotFoundException("User not found")

        return UserResponse.model_validate(user)

    async def list_users(
        self,
        *,
        search: str | None = None,
        order_by: str = "id",
        direction: str = "asc",
        limit: int = 10,
        offset: int = 0,
    ) -> list[UserResponse]:
        """查询所有用户"""
        users = await self.repository.get_all(
            search=search,
            order_by=order_by,
            direction=direction,
            limit=limit,
            offset=offset,
        )
        return [UserResponse.model_validate(user) for user in users]

    async def create_user(self, user_data: UserCreate) -> UserResponse:
        data = user_data.model_dump()
        try:
            user = await self.repository.create(data)
            return UserResponse.model_validate(user)
        except IntegrityError as e:
            raise AlreadyExistsException(
                "User with this username or email already exists"
            ) from e

    async def update_user(
        self,
        user_id: int,
        user_data: UserUpdate,
    ) -> UserResponse:
        try:
            update_data = user_data.model_dump(exclude_unset=True, exclude_none=True)
            updated = await self.repository.update(user_id, update_data)
            if not updated:
                raise NotFoundException("User not found")

            return UserResponse.model_validate(updated)
        except IntegrityError as e:
            raise AlreadyExistsException(
                "User with this username or email already exists"
            ) from e

    async def delete_user(self, user_id: int) -> bool:
        deleted = await self.repository.delete(user_id)
        if not deleted:
            raise NotFoundException("User not found")

        return True

    async def authenticate(self, username: str, password: str) -> UserResponse:
        user = await self.repository.authenticate(username, password)
        if not user:
            raise NotFoundException("Invalid username or password")

        return UserResponse.model_validate(user)

    async def verify_email(self, user_id: int) -> UserResponse:
        result = await self.repository.verify_email(user_id)
        if not result:
            raise NotFoundException("User not found")

        return UserResponse.model_validate(result)

    async def change_password(self, user_id: int, new_password: str) -> UserResponse:
        result = await self.repository.change_password(user_id, new_password)
        if not result:
            raise NotFoundException("User not found")

        return UserResponse.model_validate(result)
