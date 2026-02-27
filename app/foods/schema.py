from typing import Annotated

from sqlmodel import Field, SQLModel


class FoodCreate(SQLModel):
    name: Annotated[str, Field(..., max_length=100, description="名称")]
    brand: Annotated[str, Field(..., max_length=100, description="品牌")]
    kcals_per_g: Annotated[float | None, Field(None, ge=0, description="卡路里/克")]
    price: Annotated[float | None, Field(None, ge=0, description="价格")]
    weight: Annotated[float | None, Field(None, ge=0, description="重量")]


class FoodUpdate(SQLModel):
    name: Annotated[str | None, Field(None, max_length=100, description="名称")]
    brand: Annotated[str | None, Field(None, max_length=100, description="品牌")]
    kcals_per_g: Annotated[float | None, Field(None, ge=0, description="卡路里/克")]
    price: Annotated[float | None, Field(None, ge=0, description="价格")]
    weight: Annotated[float | None, Field(None, ge=0, description="重量")]


class FoodResponse(SQLModel):
    name: Annotated[str, Field(..., max_length=100, description="名称")]
    brand: Annotated[str, Field(..., max_length=100, description="品牌")]
    kcals_per_g: Annotated[float | None, Field(None, ge=0, description="卡路里/克")]
    price: Annotated[float | None, Field(None, ge=0, description="价格")]
    weight: Annotated[float | None, Field(None, ge=0, description="重量")]
    id: int
