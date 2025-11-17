from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from fastapi import APIRouter

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    salary = Column(Float, default=0.0)

    expenses = relationship('Expense', back_populates='user')

class Expense(Base):
    __tablename__ = 'expenses'
    expense_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(Enum('Food', 'Transport', 'Entertainment', 'Utilities', 'Other', name='expense_categories'))
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship('User', back_populates='expenses')

app = FastAPI()

# Database setup
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Pydantic models
class UserCreate(BaseModel):
    username: str
    salary: float = 0.0

class ExpenseCreate(BaseModel):
    user_id: int
    name: str
    amount: float
    category: str

# In-memory storage for users and expenses
users = []
expenses = []

@app.post('/users/', response_model=User)
async def create_user(user: UserCreate):
    users.append(user)
    return user

@app.post('/expenses/', response_model=Expense)
async def create_expense(expense: ExpenseCreate):
    expense.timestamp = datetime.now()
    expenses.append(expense)
    return expense

@app.get('/expenses/{user_id}', response_model=List[Expense])
async def list_expenses(user_id: int, day: Optional[str] = None, week: Optional[int] = None, year: Optional[int] = None, month: Optional[int] = None):
    user_expenses = [expense for expense in expenses if expense.user_id == user_id]
    # Apply filters if provided
    if day:
        user_expenses = [e for e in user_expenses if e.timestamp.date() == datetime.strptime(day, '%Y-%m-%d').date()]
    if week and year:
        user_expenses = [e for e in user_expenses if e.timestamp.isocalendar()[1] == week and e.timestamp.year == year]
    if month and year:
        user_expenses = [e for e in user_expenses if e.timestamp.month == month and e.timestamp.year == year]
    return user_expenses

@app.get('/totals/{user_id}')
async def budget_summary(user_id: int):
    user_expenses = [e for e in expenses if e.user_id == user_id]
    total_expense = sum(e.amount for e in user_expenses)
    user = next((u for u in users if u.id == user_id), None)
    total_salary = user.salary if user else 0
    remaining_amount = total_salary - total_expense
    category_breakdown = {}
    for e in user_expenses:
        category_breakdown[e.category] = category_breakdown.get(e.category, 0) + e.amount
    return {
        'total_expense': total_expense,
        'total_salary': total_salary,
        'remaining_amount': remaining_amount,
        'category_breakdown': category_breakdown
    }

router = APIRouter()

# User model
class User(BaseModel):
    username: str
    salary: Optional[float] = None

# Expense model
class Expense(BaseModel):
    user_id: int
    name: str
    amount: float
    category: str

# In-memory storage for demonstration purposes
users = []
expenses = []

@router.post("/users/")
async def create_user(user: User):
    users.append(user)
    return user

@router.post("/expenses/")
async def create_expense(expense: Expense):
    expense.timestamp = "2025-11-17T00:00:00Z"  # Placeholder timestamp
    expenses.append(expense)
    return expense

@router.get("/expenses/{user_id}", response_model=List[Expense])
async def list_expenses(user_id: int, day: Optional[str] = None, week: Optional[int] = None, year: Optional[int] = None, month: Optional[int] = None):
    user_expenses = [expense for expense in expenses if expense.user_id == user_id]
    # Apply filters if provided
    if day:
        user_expenses = [e for e in user_expenses if e.timestamp.startswith(day)]
    if week and year:
        user_expenses = [e for e in user_expenses if e.timestamp.startswith(f'{year}-W{week:02d}')]  # Placeholder for week filter
    if month and year:
        user_expenses = [e for e in user_expenses if e.timestamp.startswith(f'{year}-{month:02d}')]  # Placeholder for month filter
    return user_expenses

@router.get("/totals/{user_id}")
async def budget_summary(user_id: int):
    user_expenses = [e for e in expenses if e.user_id == user_id]
    total_expense = sum(e.amount for e in user_expenses)
    user = next((u for u in users if u.username == user_id), None)
    total_salary = user.salary if user else 0
    remaining_amount = total_salary - total_expense
    category_breakdown = {}
    for e in user_expenses:
        category_breakdown[e.category] = category_breakdown.get(e.category, 0) + e.amount
    return {
        "total_expense": total_expense,
        "total_salary": total_salary,
        "remaining_amount": remaining_amount,
        "category_breakdown": category_breakdown
    }
