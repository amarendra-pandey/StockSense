from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models import Holding, User


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    Base.metadata.drop_all(engine)
    engine.dispose()


def test_user_and_holding_relationship_persists(db_session):
    user = User(email="investor@example.com", hashed_password="hashed-value")
    user.holdings.append(
        Holding(
            symbol="RELIANCE",
            quantity=Decimal("2.5"),
            average_buy_price=Decimal("1250.75"),
        )
    )
    db_session.add(user)
    db_session.commit()

    saved_user = db_session.query(User).filter_by(email="investor@example.com").one()

    assert saved_user.holdings[0].symbol == "RELIANCE"
    assert saved_user.holdings[0].quantity == Decimal("2.500000")
    assert saved_user.holdings[0].average_buy_price == Decimal("1250.7500")
    assert saved_user.holdings[0].user is saved_user


def test_user_email_is_unique(db_session):
    db_session.add_all(
        [
            User(email="investor@example.com", hashed_password="hashed-one"),
            User(email="investor@example.com", hashed_password="hashed-two"),
        ]
    )

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


@pytest.mark.parametrize(
    ("quantity", "average_buy_price"),
    [
        (Decimal("0"), Decimal("1")),
        (Decimal("1"), Decimal("0")),
        (Decimal("-1"), Decimal("1")),
        (Decimal("1"), Decimal("-1")),
    ],
)
def test_holding_requires_positive_quantity_and_price(
    db_session,
    quantity,
    average_buy_price,
):
    user = User(email="investor@example.com", hashed_password="hashed-value")
    db_session.add(user)
    db_session.flush()
    db_session.add(
        Holding(
            user_id=user.id,
            symbol="RELIANCE",
            quantity=quantity,
            average_buy_price=average_buy_price,
        )
    )

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()
