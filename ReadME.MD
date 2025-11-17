Designed specifically for the **FastAPI Machine Test – Python Developer**.

---

## 📌 Features

- Create Users  
- Track Expenses per User  
- Filter Expenses by:
  - Day (YYYY-MM-DD)
  - Week + Year
  - Month + Year
  - Category
- View Budget Summary
- SQLite + SQLAlchemy ORM
- Asynchronous FastAPI  
- Only 3 files: `main.py`, `schemas.py`, `services.py`

---

## 📁 Project Structure

```

.
├── main.py  # API routes
app_      
    ├── schemas.py     # Pydantic request/response schemas
    ├── services.py    # DB models, async engine, business logic

````

---

## ⚙️ Setup Instructions

### 1️⃣ Install Dependencies
```bash
pip install fastapi "uvicorn[standard]" sqlalchemy aiosqlite pydantic
````

### 2️⃣ Run the Server

```bash
uvicorn main:app --reload
```

### 3️⃣ Open the Automatic API Docs

👉 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🧪 Example Test Data (Very Simple Examples)

### 👤 **Create User**

**POST /users/**

```json
{
  "username": "john",
  "salary": 50000
}
```

**Response**

```json
{
  "user_id": 1,
  "username": "john",
  "salary": 50000
}
```

---

### 💸 **Create Expense**

| Field    | Example |
| -------- | ------- |
| user_id  | 1       |
| name     | "Lunch" |
| amount   | 150     |
| category | "Food"  |

**POST /expenses/**

```json
{
  "user_id": 1,
  "name": "Lunch",
  "amount": 150,
  "category": "Food"
}
```

**Response**

```json
{
  "expense_id": 1,
  "user_id": 1,
  "name": "Lunch",
  "amount": 150,
  "category": "Food",
  "created_at": "2025-11-17T10:25:30.000Z"
}
```

---

## 📚 All Endpoints

### 1️⃣ **Create User**

**POST /users/**
Body:

```json
{
  "username": "alex",
  "salary": 30000
}
```

---

### 2️⃣ **Create Expense**

**POST /expenses/**
Body:

```json
{
  "user_id": 1,
  "name": "Taxi",
  "amount": 200,
  "category": "Transport"
}
```

---

### 3️⃣ **List User Expenses**

**GET /expenses/{user_id}**

#### Filters you can use:

```
/expenses/1?day=2025-11-17
/expenses/1?week=46&year=2025
/expenses/1?month=11&year=2025
/expenses/1?category=Food
```

---

### 4️⃣ **Budget Summary**

**GET /totals/{user_id}**

**Example Response**

```json
{
  "total_salary": 50000,
  "total_expense": 3200,
  "remaining_amount": 46800,
  "category_breakdown": {
    "Food": 1200,
    "Transport": 800,
    "Entertainment": 1200
  }
}
```

---

## 🧠 How the System Works (Very Simple)

1. **Create a user** → stores username + salary
2. **Add expenses** → linked to the user by `user_id`
3. **List expenses** → filter by day/week/month/category
4. **Budget summary** → calculates:

   * Total spent
   * Remaining salary
   * Category breakdown

---
flowchart LR
  subgraph Client
    A[User / Client (Postman / Browser)]
  end

  subgraph API["FastAPI App\n(main.py)"]
    direction TB
    B1[Routes\nPOST /users\nPOST /expenses\nGET /expenses/{user_id}\nGET /totals/{user_id}]
    B2[schemas.py\nPydantic validation]
    B3[services.py\nSQLAlchemy models + async DB + business logic]
  end

  subgraph DB["SQLite DB\n(test.db)"]
    C[SQLite (aiosqlite) file]
  end

  subgraph Infra["Optional: Docker"]
    D[Dockerfile / compose]
  end

  A -->|HTTP JSON| B1
  B1 --> B2
  B1 --> B3
  B3 -->|async SQL| C
  D -.-> B1

  classDef app fill:#f8f9fa,stroke:#333,stroke-width:1px;
  class API app;
  style DB fill:#fff3cd,stroke:#c69500
  style Infra fill:#e6f0ff,stroke:#2b6cb0
---
## ✅ This Project Covers All Machine Test Requirements

✔ SQLAlchemy ORM
✔ Async FastAPI
✔ Correct validations
✔ Filtering logic
✔ Clean, simple structure
✔ Ready to extend (JWT, Alembic, etc.)

---

## 📞 Need enhancements?

If you'd like:

* JWT Authentication
* Docker deployment
* Alembic migrations
* Unit tests
