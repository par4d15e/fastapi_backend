from sqlmodel import Field, Index, SQLModel, desc

from app.core.base_model import DateTimeMixin


class Food(DateTimeMixin, SQLModel, table=True):
    __tablename__ = "foods"  # type: ignore[assignment]
    __table_args__ = (
        # 复合索引
        Index("idx_foods_brand_name", "brand", "name"),  # 按品牌+名称筛选
        Index("idx_foods_brand_price", "brand", "price"),  # 按品牌+价格筛选
        # 排序索引
        Index("idx_foods_created_at_desc", desc("created_at")),
        Index("idx_foods_updated_at_desc", desc("updated_at")),
    )

    id: int | None = Field(default=None, primary_key=True, description="编号")

    name: str = Field(..., max_length=100, unique=True, index=True, description="名称")

    brand: str = Field(..., max_length=100, description="品牌")
    metabolic_energy: float | None = Field(
        default=None, ge=0, index=True, description="代谢能(卡路里/千克)"
    )

    price: float | None = Field(default=None, ge=0, index=True, description="价格")

    weight: float | None = Field(
        default=None, ge=0, index=True, description="重量(千克)"
    )

    description: str | None = Field(default=None, max_length=255, description="描述")

    def __repr__(self) -> str:  # pragma: no cover - simple representation
        return f"<Food(id={self.id}, name={self.name})>"
