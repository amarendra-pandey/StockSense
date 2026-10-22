from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ORMResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserResponse(ORMResponse):
    id: int
    email: EmailStr


class HoldingCreate(BaseModel):
    symbol: str = Field(min_length=1, max_length=32)
    quantity: Decimal = Field(gt=0, max_digits=18, decimal_places=6)
    average_buy_price: Decimal = Field(gt=0, max_digits=18, decimal_places=4)


class HoldingResponse(ORMResponse):
    id: int
    user_id: int
    symbol: str
    quantity: Decimal
    average_buy_price: Decimal
