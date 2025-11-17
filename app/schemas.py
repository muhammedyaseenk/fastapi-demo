from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional, Dict

ALLOWED_CATEGORIES = {"Food", "Transport", "Entertainment", "Utilities", "Other"}

# ---------- User schemas ----------
class UserCreate(BaseModel):
    username: str
    salary: Optional[float] = 0.0

    @validator("salary")
    def salary_non_negative(cls, v):
        if v is not None and v < 0:
            raise ValueError("salary must be >= 0")
        return v


class UserOut(BaseModel):
    user_id: int
    username: str
    salary: float

    class Config:
        orm_mode = True


# ---------- Expense schemas ----------
class ExpenseCreate(BaseModel):
    user_id: int
    name: str
    amount: float
    category: str

    @validator("amount")
    def amount_positive(cls, v):
        if v <= 0:
            raise ValueError("amount must be greater than 0")
        return v

    @validator("category")
    def valid_category(cls, v):
        if v not in ALLOWED_CATEGORIES:
            raise ValueError(f"category must be one of {sorted(ALLOWED_CATEGORIES)}")
        return v


class ExpenseOut(BaseModel):
    expense_id: int
    user_id: int
    name: str
    amount: float
    category: str
    created_at: datetime

    class Config:
        orm_mode = True


# ---------- Totals response ----------
class TotalsOut(BaseModel):
    total_salary: float
    total_expense: float
    remaining_amount: float
    category_breakdown: Dict[str, float]
