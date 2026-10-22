from decimal import Decimal

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))

    holdings: Mapped[list["Holding"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Holding(Base):
    __tablename__ = "holdings"
    __table_args__ = (
        UniqueConstraint("user_id", "symbol", name="uq_holdings_user_symbol"),
        CheckConstraint("quantity > 0", name="ck_holdings_quantity_positive"),
        CheckConstraint(
            "average_buy_price > 0",
            name="ck_holdings_average_buy_price_positive",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
    )
    symbol: Mapped[str] = mapped_column(String(32))
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 6))
    average_buy_price: Mapped[Decimal] = mapped_column(Numeric(18, 4))

    user: Mapped[User] = relationship(back_populates="holdings")
