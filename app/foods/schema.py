from sqlmodel import Field, SQLModel


class FoodCreate(SQLModel):
    name: str = Field(..., max_length=100, description="名称")
    brand: str = Field(..., max_length=100, description="品牌")
    metabolic_energy: float | None = Field(
        None, ge=0, description="代谢能(卡路里/千克)"
    )
    price: float | None = Field(None, ge=0, description="价格")
    weight: float | None = Field(None, ge=0, description="重量(千克)")
    description: str | None = Field(None, max_length=255, description="描述")


class FoodUpdate(SQLModel):
    name: str | None = Field(None, max_length=100, description="名称")
    brand: str | None = Field(None, max_length=100, description="品牌")
    metabolic_energy: float | None = Field(
        None, ge=0, description="代谢能(卡路里/千克)"
    )
    price: float | None = Field(None, ge=0, description="价格")
    weight: float | None = Field(None, ge=0, description="重量(千克)")
    description: str | None = Field(None, max_length=255, description="描述")


class FoodResponse(SQLModel):
    id: int
    name: str = Field(..., max_length=100, description="名称")
    brand: str = Field(..., max_length=100, description="品牌")
    metabolic_energy: float | None = Field(
        None, ge=0, description="代谢能(卡路里/千克)"
    )
    price: float | None = Field(None, ge=0, description="价格")
    weight: float | None = Field(None, ge=0, description="重量(千克)")
    description: str | None = Field(None, max_length=255, description="描述")
