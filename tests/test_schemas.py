from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.models import Holding, User
from app.schemas import HoldingCreate, HoldingResponse, UserCreate, UserResponse


def test_user_create_validates_email_and_accepts_password():
    user = UserCreate(email="investor@example.com", password="plain-password")

    assert user.email == "investor@example.com"
    assert user.password == "plain-password"


def test_user_response_serializes_orm_without_password_hash():
    user = User(id=1, email="investor@example.com", hashed_password="secret-hash")

    response = UserResponse.model_validate(user)

    assert response.model_dump() == {"id": 1, "email": "investor@example.com"}
    assert "hashed_password" not in response.model_dump()


def test_holding_create_requires_positive_values():
    holding = HoldingCreate(
        symbol="RELIANCE",
        quantity=Decimal("2.5"),
        average_buy_price=Decimal("1250.75"),
    )

    assert holding.quantity == Decimal("2.5")
    assert holding.average_buy_price == Decimal("1250.75")

    with pytest.raises(ValidationError):
        HoldingCreate(symbol="RELIANCE", quantity=0, average_buy_price=1250)


def test_holding_response_serializes_orm():
    holding = Holding(
        id=1,
        user_id=2,
        symbol="RELIANCE",
        quantity=Decimal("2.5"),
        average_buy_price=Decimal("1250.75"),
    )

    response = HoldingResponse.model_validate(holding)

    assert response.model_dump() == {
        "id": 1,
        "user_id": 2,
        "symbol": "RELIANCE",
        "quantity": Decimal("2.5"),
        "average_buy_price": Decimal("1250.75"),
    }
