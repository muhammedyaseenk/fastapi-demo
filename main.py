from fastapi import FastAPI, Depends, HTTPException, status
from typing import List, Optional
import uvicorn

from app.schemas import (
    UserCreate, UserOut,
    ExpenseCreate, ExpenseOut,
    TotalsOut
)
from app.services import get_db
from app import services
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI(title="Expense & Budget Manager (Simple 3-file)")


#  make a get
@app.get("/")
async def root():
    return {"message": "Your frind Muhammed Yaseen here! Welcome to the Expense & Budget Manager API."}

# initialize DB tables
@app.on_event("startup")
async def on_startup():
    await services.init_db()


# Create user
@app.post("/users/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        user = await services.create_user(db, username=payload.username, salary=payload.salary or 0.0)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Create expense
@app.post("/expenses/", response_model=ExpenseOut, status_code=status.HTTP_201_CREATED)
async def create_expense(payload: ExpenseCreate, db: AsyncSession = Depends(get_db)):
    try:
        exp = await services.create_expense(
            db,
            user_id=payload.user_id,
            name=payload.name,
            amount=payload.amount,
            category=payload.category
        )
        return exp
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# List expenses with filters
@app.get("/expenses/{user_id}", response_model=List[ExpenseOut])
async def get_expenses(
    user_id: int,
    day: Optional[str] = None,
    week: Optional[int] = None,
    year: Optional[int] = None,
    month: Optional[int] = None,
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    # returns [] if user exists but no expenses; raise 404 if user not found
    user = await db.get(services.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    expenses = await services.list_expenses(db, user_id, day, week, year, month, category)
    return expenses


# Totals / budget summary
@app.get("/totals/{user_id}", response_model=TotalsOut)
async def totals(user_id: int, db: AsyncSession = Depends(get_db)):
    try:
        data = await services.budget_summary(db, user_id)
        return data
    except LookupError:
        raise HTTPException(status_code=404, detail="user not found")


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
