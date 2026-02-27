from typing import Annotated

from sqlmodel import Field, SQLModel

from app.core.base_model import DateTimeMixin


class Food(SQLModel, table=True, mixins=[DateTimeMixin]):
    __tablename__ = "foods" # type: ignore[assignment]

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