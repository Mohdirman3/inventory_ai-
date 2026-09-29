# 📦 Inventory AI

A full-stack inventory management system built with **Flask** (Backend) and **React + Vite** (Frontend), backed by **MySQL**. Built as a portfolio project demonstrating real-world backend architecture, transactional data integrity, JWT-based authentication, role-based access control, and analytics-driven business intelligence.

---

## ✨ Features

| Area | What it does |
|---|---|
| **Products & Suppliers** | Full CRUD with soft-delete pattern to preserve historical data integrity |
| **Inventory Control** | Set, add, and remove stock with hard floor at zero |
| **Sales Recording** | Atomic transactions — sale record and stock decrement always happen together or not at all |
| **Purchase Orders** | Multi-item orders with atomic stock increment on receiving |
| **Smart Analytics** | Inventory summary, top-selling products, reorder recommendations (daily rate × lead time formula), supplier performance |
| **Authentication** | JWT tokens (24h expiry), bcrypt password hashing, two-role RBAC (ADMIN / EMPLOYEE) |
| **API Documentation** | Full endpoint reference in [API.md](./API.md) |
| **Automated Tests** | 21 pytest tests covering auth, products, and atomic sales transactions |
| **Database Migrations** | Alembic version-controlled schema management |
| **Performance** | B-Tree indexes on all frequently queried and joined columns |

---

## 🛠 Tech Stack

### Backend
| Tool | Role |
|---|---|
| **Python 3.13** | Language |
| **Flask 3** | Web framework |
| **SQLAlchemy 2** | ORM |
| **PyMySQL** | MySQL driver |
| **MySQL** | Relational database |
| **PyJWT** | JWT token signing |
| **Werkzeug** | Password hashing |
| **Alembic** | Database migrations |
| **pytest** | Automated testing |

### Frontend
| Tool | Role |
|---|---|
| **React 19** | UI framework |
| **Vite 8** | Dev server & bundler |
| **React Router v7** | Client-side routing |
| **Axios** | HTTP client with JWT interceptor |
| **Recharts** | Dashboard charts |
| **react-hot-toast** | Toast notifications |

---

## 📁 Project Structure

```
inventory_ai/
├── API.md                          ← Full API endpoint documentation
├── backend/
│   ├── .env                        ← Secrets (DB credentials, SECRET_KEY) — not committed
│   ├── requirements.txt            ← Python dependencies
│   ├── alembic/                    ← Database migration scripts
│   │   └── versions/               ← Auto-generated migration files
│   ├── tests/                      ← pytest test suite
│   │   ├── conftest.py             ← Shared fixtures (test client, JWT tokens)
│   │   ├── test_auth.py            ← Auth & RBAC tests
│   │   ├── test_products.py        ← Product endpoint tests
│   │   └── test_sales.py           ← Atomic transaction tests
│   └── app/
│       ├── main.py                 ← App factory, CORS, Blueprint registration
│       ├── core/
│       │   └── config.py           ← Loads environment variables
│       ├── database/
│       │   ├── connection.py       ← SQLAlchemy engine & session
│       │   ├── models.py           ← All 7 database models
│       │   └── add_indexes.py      ← One-time index creation script
│       └── routes/
│           ├── auth.py             ← Register, login, JWT decorators
│           ├── products.py         ← Product CRUD
│           ├── suppliers.py        ← Supplier CRUD
│           ├── inventory.py        ← Stock management
│           ├── sales.py            ← Atomic sale recording
│           ├── purchase_orders.py  ← Purchase orders & receiving
│           └── analytics.py        ← Dashboard metrics & reorder logic
└── frontend/
    ├── vite.config.js              ← Runs on port 3000
    └── src/
        ├── api/axios.js            ← Central Axios client + auto JWT injection
        ├── components/
        │   ├── Navbar.jsx          ← Navigation with active link highlighting
        │   └── ProtectedRoute.jsx  ← Redirects unauthenticated users to /login
        └── pages/
            ├── Home.jsx            ← Public landing page
            ├── Login.jsx / Register.jsx
            ├── Dashboard.jsx       ← Stat cards + bar/pie charts
            ├── Products.jsx        ← Table with modal-based CRUD
            ├── Suppliers.jsx       ← Same CRUD pattern
            ├── Inventory.jsx       ← Stock levels, add/remove/set
            ├── Sales.jsx           ← Sale history + record new sale
            ├── PurchaseOrders.jsx  ← Expandable order cards + receive button
            └── profile.jsx         ← Edit name, email, password
```

---

## ⚙️ Setup & Running Locally

### Prerequisites
- Python 3.10+
- Node.js 18+
- MySQL 8.0+ (running locally)
- MySQL database named `inventory_ai`

---

### 1. Backend Setup

```powershell
# Navigate to backend
cd inventory_ai/backend

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1   # Windows
# source venv/bin/activate    # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Create your .env file (copy the template below)
```

Create `backend/.env`:
```env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=inventory_ai
DB_USER=root
DB_PASSWORD=your_mysql_password
SECRET_KEY=some-long-random-secret-key-here
```

```powershell
# Start the Flask server
python -m app.main
```
Backend runs at: **`http://127.0.0.1:8001`**

---

### 2. Database Migrations

```powershell
# Apply schema (first time)
alembic upgrade head

# (If tables already exist, stamp as baseline instead)
alembic stamp head
```

---

### 3. Frontend Setup

```powershell
# Navigate to frontend
cd inventory_ai/frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```
Frontend runs at: **`http://localhost:3000`**

---

## ✅ Running Tests

```powershell
cd inventory_ai/backend
.\venv\Scripts\Activate.ps1
python -m pytest tests/ -v
```

**21 tests** across 3 suites:
- `test_auth.py` — Login, registration, token validation, RBAC (401/403)
- `test_products.py` — Public endpoints, auth barriers, input validation
- `test_sales.py` — **Atomic transaction verification**: confirms inventory decrements correctly on every sale

---

## 🔑 Key Architecture Decisions

**Why soft delete?**
Deleting a product that has historical sales would break those records (orphaned foreign keys). Setting `is_active = False` preserves all historical data while hiding the item from active lists.

**Why transactions on Sales and Purchase Orders?**
Two things must happen together: create a ledger record AND update stock quantity. A crash between them leaves the database inconsistent. SQLAlchemy's session commit groups both writes atomically — either both succeed or both roll back.

**Why JWT over sessions?**
Sessions require server-side storage that doesn't scale horizontally. JWTs are stateless — any server instance can validate them without a shared store.

**Reorder recommendation formula:**
$$\text{Reorder} \iff \text{Current Stock} \leq \text{Daily Sales Rate} \times \text{Supplier Lead Time (days)}$$

---

## 📄 API Reference

See [API.md](./API.md) for the complete endpoint reference including request/response examples, query parameters, and status codes.

---

## 🗂 Database Schema

```
products ──────────── suppliers
    │
    ├── inventory (1:1)
    ├── sales (1:many)
    └── purchase_order_items (many)
            │
        purchase_orders ── suppliers
```

7 tables: `users`, `products`, `suppliers`, `inventory`, `sales`, `purchase_orders`, `purchase_order_items`
