from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import Holding, User
from app.schemas import HoldingCreate, HoldingResponse

app = FastAPI(title=settings.app_name, debug=settings.debug)
app.state.environment = settings.environment


@app.get("/health", status_code=200)
async def health_check():
    return {"status": "ok", "method": "GET", "status_code": 200}


@app.get(
    "/users/{user_id}/holdings",
    response_model=list[HoldingResponse],
)
def list_holdings(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    statement = (
        select(Holding)
        .where(Holding.user_id == user_id)
        .order_by(Holding.id)
    )
    return db.scalars(statement).all()


@app.post(
    "/users/{user_id}/holdings",
    response_model=HoldingResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_holding(
    user_id: int,
    holding_data: HoldingCreate,
    db: Session = Depends(get_db),
):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    holding = Holding(user_id=user_id, **holding_data.model_dump())
    db.add(holding)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Holding conflicts with existing data",
        ) from exc

    db.refresh(holding)
    return holding
