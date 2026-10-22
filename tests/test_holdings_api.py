from collections.abc import Generator
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Holding, User


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)

    def override_get_db() -> Generator[Session, None, None]:
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    with Session(engine) as session:
        session.add(
            User(
                id=1,
                email="investor@example.com",
                hashed_password="hashed-value",
                holdings=[
                    Holding(
                        symbol="RELIANCE",
                        quantity=Decimal("2.5"),
                        average_buy_price=Decimal("1250.75"),
                    )
                ],
            )
        )
        session.commit()

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)
    engine.dispose()


def test_list_holdings_returns_only_user_holdings(client):
    response = client.get("/users/1/holdings")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "user_id": 1,
            "symbol": "RELIANCE",
            "quantity": "2.500000",
            "average_buy_price": "1250.7500",
        }
    ]


def test_create_holding_persists_and_returns_holding(client):
    response = client.post(
        "/users/1/holdings",
        json={
            "symbol": "TCS",
            "quantity": "3",
            "average_buy_price": "4000.25",
        },
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": 2,
        "user_id": 1,
        "symbol": "TCS",
        "quantity": "3.000000",
        "average_buy_price": "4000.2500",
    }


def test_create_holding_rejects_duplicate_symbol_for_user(client):
    response = client.post(
        "/users/1/holdings",
        json={
            "symbol": "RELIANCE",
            "quantity": "1",
            "average_buy_price": "1200",
        },
    )

    assert response.status_code == 409


@pytest.mark.parametrize("method", ["get", "post"])
def test_holdings_endpoints_return_404_for_missing_user(client, method):
    if method == "post":
        response = client.post(
            "/users/999/holdings",
            json={
                "symbol": "TCS",
                "quantity": "1",
                "average_buy_price": "4000",
            },
        )
    else:
        response = client.get("/users/999/holdings")

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


def test_create_holding_validates_request(client):
    response = client.post(
        "/users/1/holdings",
        json={
            "symbol": "TCS",
            "quantity": "0",
            "average_buy_price": "4000",
        },
    )

    assert response.status_code == 422
