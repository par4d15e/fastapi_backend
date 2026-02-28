"""Token and verification code CRUD operations - sqlmodel"""

import secrets
from datetime import datetime, timedelta, timezone

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.auth.model import Code, CodeType, RefreshToken


class RefreshTokenCRUD:
    """刷新令牌 CRUD 操作类"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        user_id: int,
        jti: str,
        token: str,
        expired_at: datetime,
        is_active: bool = True,
    ) -> RefreshToken:
        """创建新的刷新令牌记录

        新模型只包含 jti、token、user_id、expires_at 和 is_active 字段。
        jti 必须由调用方生成并保证唯一性
        """
        db_token = RefreshToken(
            user_id=user_id,
            jti=jti,
            token=token,
            expired_at=expired_at,
            is_active=is_active,
            created_at=datetime.now(timezone.utc),
        )

        self.session.add(db_token)
        await self.session.commit()
        await self.session.refresh(db_token)
        return db_token

    async def get_by_token(self, token: str) -> RefreshToken | None:
        """根据令牌字符串获取刷新令牌（仅限活动状态）"""
        statement = select(RefreshToken).where(
            RefreshToken.token == token,
            RefreshToken.is_active.is_(True),  # type: ignore
        )
        result = await self.session.exec(statement)
        return result.one_or_none()

    async def get_user_tokens(
        self, user_id: int, include_inactive: bool = False
    ) -> list[RefreshToken]:
        """获取属于指定用户的所有刷新令牌

        默认只返回 `is_active=True` 的令牌，除非
        `include_inactive=True`
        """
        statement = select(RefreshToken).where(RefreshToken.user_id == user_id)

        if not include_inactive:
            statement = statement.where(RefreshToken.is_active.is_(True))  # type: ignore

        result = await self.session.exec(statement)
        return list(result.all())

    async def revoke(self, token: str) -> bool:
        """将指定令牌标记为不活动（`is_active=False`）。"""
        db_token = await self.get_by_token(token)
        if not db_token:
            return False

        db_token.is_active = False
        await self.session.commit()
        return True

    async def revoke_user_tokens(self, user_id: int) -> int:
        """将用户的所有活动令牌标记为不活动，返回受影响数量。"""
        tokens = await self.get_user_tokens(user_id, include_inactive=False)

        count = 0
        for token in tokens:
            token.is_active = False
            count += 1

        await self.session.commit()
        return count

    async def cleanup_expired(self) -> int:
        """将所有过期且仍然活跃的令牌标记为不活动"""
        statement = select(RefreshToken).where(
            RefreshToken.expired_at < datetime.now(timezone.utc),
            RefreshToken.is_active.is_(True),  # type: ignore
        )
        result = await self.session.exec(statement)
        expired_tokens = list(result.all())

        count = 0
        for token in expired_tokens:
            token.is_active = False
            count += 1

        await self.session.commit()
        return count


class CodeCRUD:
    """验证码/Code CRUD 操作类"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def generate_code(self, length: int = 6) -> str:
        """生成数字验证码"""
        return "".join([str(secrets.randbelow(10)) for _ in range(length)])

    async def create(
        self,
        user_id: int,
        code_type: CodeType,
        expiration_minutes: int = 60,
    ) -> Code:
        """创建验证码记录"""
        code = self.generate_code()

        db_code = Code(
            user_id=user_id,
            code=code,
            type=code_type,
            expires_at=datetime.now(timezone.utc)
            + timedelta(minutes=expiration_minutes),
            created_at=datetime.now(timezone.utc),
        )

        self.session.add(db_code)
        await self.session.commit()
        await self.session.refresh(db_code)
        return db_code

    async def get(self, user_id: int, code: str, code_type: CodeType) -> Code | None:
        """获取验证码"""
        statement = select(Code).where(
            Code.user_id == user_id,
            Code.code == code,
            Code.type == code_type,
            Code.is_used.is_(False),  # type: ignore
        )
        result = await self.session.exec(statement)
        return result.one_or_none()

    async def verify(self, user_id: int, code: str, code_type: CodeType) -> Code | None:
        """验证验证码并标记为已使用

        如果记录不存在或已被标记过，返回 `None`
        """
        db_code = await self.get(user_id, code, code_type)

        if not db_code:
            return None

        # mark as used and persist
        db_code.is_used = True
        await self.session.commit()
        await self.session.refresh(db_code)
        return db_code

    async def get_latest(self, user_id: int, code_type: CodeType) -> Code | None:
        """获取用户最新的验证码"""
        statement = (
            select(Code)
            .where(
                Code.user_id == user_id,
                Code.type == code_type,
            )
            .order_by(Code.created_at.desc())  # type: ignore
        )
        result = await self.session.exec(statement)
        return result.one_or_none()

    async def invalidate_user_codes(self, user_id: int, code_type: CodeType) -> int:
        """将用户所有未使用的验证码标记为已使用"""
        statement = select(Code).where(
            Code.user_id == user_id,
            Code.type == code_type,
            Code.is_used.is_(False),  # type: ignore
        )
        result = await self.session.exec(statement)
        codes = list(result.all())

        count = 0
        for code in codes:
            code.is_used = True
            count += 1

        await self.session.commit()
        return count

    async def cleanup_expired(self) -> int:
        """将过期且仍未使用的验证码标记为已使用"""
        statement = select(Code).where(
            Code.expires_at < datetime.now(timezone.utc),
            Code.is_used.is_(False),  # type: ignore
        )
        result = await self.session.exec(statement)
        expired_codes = list(result.all())

        count = 0
        for code in expired_codes:
            code.is_used = True
            count += 1

        await self.session.commit()
        return count
