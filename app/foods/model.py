from typing import Annotated

from sqlmodel import Field, Index, SQLModel, desc

from app.core.base_model import DateTimeMixin


class Food(SQLModel, table=True, mixins=[DateTimeMixin]):
    __tablename__ = "foods"  # type: ignore[assignment]
    __table_args__ = (
        # 单列索引
        Index("idx_foods_name", "name"),
        Index("idx_foods_brand", "brand"),
        # 复合索引 - 用于高效查询
        Index("idx_foods_brand_name", "brand", "name"),  # 按品牌查询食品列表
        Index("idx_foods_brand_price", "brand", "price"),  # 按品牌筛选价格区间
        Index("idx_foods_kcals_per_g", "kcals_per_g"),  # 按卡路里筛选
        # 排序索引
        Index("idx_foods_created_at_desc", desc("created_at")),
        Index("idx_foods_updated_at_desc", desc("updated_at")),
        Index("idx_foods_price_asc", "price"),  # 按价格排序
    )

    id: Annotated[int, Field(default=None, primary_key=True, description="编号")]
    name: Annotated[
        str, Field(..., max_length=100, index=True, unique=True, description="名称")
    ]
    brand: Annotated[str, Field(..., max_length=100, index=True, description="品牌")]
    kcals_per_g: Annotated[
        float | None, Field(default=None, ge=0, description="卡路里/克")
    ]
    price: Annotated[float | None, Field(default=None, ge=0, description="价格")]
    weight: Annotated[float | None, Field(default=None, ge=0, description="重量")]
    description: Annotated[
        str | None, Field(default=None, max_length=255, description="描述")
    ]

    def __repr__(self) -> str:  # pragma: no cover - simple representation
        return f"<Food(id={self.id}, name={self.name}, brand={self.brand})>"
