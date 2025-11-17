from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy import (
    Column, Integer, String, Float, ForeignKey, Enum, DateTime, func, select
)
from typing import AsyncGenerator, List, Optional
from datetime import datetime
import enum

DATABASE_URL = "sqlite+aiosqlite:///./test.db"
engine = create_async_engine(DATABASE_URL, future=True, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


# SQLAlchemy category enum (string)
class CategoryEnum(enum.Enum):
    Food = "Food"
    Transport = "Transport"
    Entertainment = "Entertainment"
    Utilities = "Utilities"
    Other = "Other"


class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    salary = Column(Float, default=0.0)
    expenses = relationship("Expense", back_populates="user")


class Expense(Base):
    __tablename__ = "expenses"
    expense_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(Enum(CategoryEnum), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="expenses")


# DB helpers
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


# Create DB tables (call at startup)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# CRUD helpers
async def create_user(db: AsyncSession, username: str, salary: float):
    # check existing
    q = select(User).where(User.username == username)
    res = await db.execute(q)
    if res.scalar_one_or_none():
        raise ValueError("username already exists")
    user = User(username=username, salary=salary)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def create_expense(db: AsyncSession, user_id: int, name: str, amount: float, category: str):
    # ensure user exists
    user = await db.get(User, user_id)
    if not user:
        raise LookupError("user not found")
    # create
    exp = Expense(
        user_id=user_id,
        name=name,
        amount=amount,
        category=CategoryEnum(category)
    )
    db.add(exp)
    await db.commit()
    await db.refresh(exp)
    return exp


async def list_expenses(
    db: AsyncSession,
    user_id: int,
    day: Optional[str] = None,
    week: Optional[int] = None,
    year: Optional[int] = None,
    month: Optional[int] = None,
    category: Optional[str] = None,
) -> List[Expense]:
    q = select(Expense).where(Expense.user_id == user_id).order_by(Expense.created_at.desc())
    res = await db.execute(q)
    rows = res.scalars().all()

    # If no filters, return early
    if not any([day, week, month, year, category]):
        return rows

    filtered = rows

    if day:
        target = datetime.strptime(day, "%Y-%m-%d").date()
        filtered = [e for e in filtered if e.created_at.date() == target]

    if week and year:
        filtered = [e for e in filtered if e.created_at.isocalendar()[1] == week and e.created_at.year == year]

    if month and year:
        filtered = [e for e in filtered if e.created_at.month == month and e.created_at.year == year]

    if category:
        filtered = [e for e in filtered if e.category.value == category]

    return filtered


async def budget_summary(db: AsyncSession, user_id: int):
    user = await db.get(User, user_id)
    if not user:
        raise LookupError("user not found")

    q = select(Expense).where(Expense.user_id == user_id)
    res = await db.execute(q)
    expenses = res.scalars().all()

    total_expense = sum(e.amount for e in expenses)
    total_salary = user.salary or 0.0
    remaining = total_salary - total_expense

    breakdown = {}
    for e in expenses:
        k = e.category.value
        breakdown[k] = breakdown.get(k, 0.0) + e.amount

    return {
        "total_salary": total_salary,
        "total_expense": total_expense,
        "remaining_amount": remaining,
        "category_breakdown": breakdown
    }
