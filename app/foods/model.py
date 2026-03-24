from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Float, ForeignKey, Index, String, desc
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base_model import Base, DateTimeMixin

if TYPE_CHECKING:
    from app.auth.model import User


class Food(DateTimeMixin, Base):
    __tablename__ = "foods"
    __table_args__ = (
        # 复合索引
        Index("idx_foods_brand_name", "brand", "name"),  # 按品牌+名称筛选
        Index("idx_foods_brand_price", "brand", "price"),  # 按品牌+价格筛选
        # 排序索引
        Index("idx_foods_created_at_desc", desc("created_at")),
        Index("idx_foods_updated_at_desc", desc("updated_at")),
    )

    id: Mapped[int] = mapped_column(primary_key=True, comment="编号")
    name: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, comment="名称"
    )
    brand: Mapped[str] = mapped_column(String(100), comment="品牌")
    metabolic_energy: Mapped[float | None] = mapped_column(
        Float, index=True, comment="代谢能(卡路里/千克)"
    )
    price: Mapped[float | None] = mapped_column(Float, index=True, comment="价格")
    weight: Mapped[float | None] = mapped_column(
        Float, index=True, comment="重量(千克)"
    )
    description: Mapped[str | None] = mapped_column(String(255), comment="描述")

    # 外键及关系（与 User 关联）
    user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("user.id"), index=True, comment="所属用户ID"
    )
    user: Mapped[User | None] = relationship("User", back_populates="foods")

    def __repr__(self) -> str:  # pragma: no cover - simple representation
        return f"<Food(id={self.id}, name={self.name})>"
