# 📦 Inventory AI — Enterprise Inventory & Management System

An enterprise-ready inventory tracking and AI management platform featuring **Role-Based Access Control (RBAC)**, **atomic database transactions**, **real-time turnover analytics**, **automated purchase order workflows**, and **high-performance indexed MySQL storage**.

---

## 🏗️ Architecture & Technology Stack

| Layer | Technologies | Description |
|---|---|---|
| **Frontend** | React 19, Vite, Tailwind CSS, Recharts, React Router v7, Axios | Responsive Single Page Application (SPA) with interactive telemetry and charts |
| **Backend** | Python 3.13, Flask 3.1, SQLAlchemy 2.0, PyMySQL | Modular REST API with Blueprint architecture and connection pooling |
| **Database** | MySQL 8.0, Alembic | Relational database with B-Tree indexes and versioned schema migrations |
| **Security** | PyJWT (`HS256`), salted password hashing, RBAC | Strict route protection separating `ADMIN` and `EMPLOYEE` operations |
| **Testing** | Pytest 9.1 | Automated integration test suite covering auth, products, transactions |

---

## 🎯 Key Capabilities & Technical Highlights

### 1. 🔄 Atomic Transaction Management (ACID)
- **Point-of-Sale Execution**: Recording a sale atomically updates sales ledger entries and deducts quantities from the `inventory` table in a single atomic transaction. Prevents phantom stock drops or overselling.
- **Purchase Order Receipt**: Receiving a vendor PO automatically credits inventory stock and transitions order status cleanly.

### 2. 🔐 Role-Based Access Control (RBAC)
- **`ADMIN`**: Full administrative privileges over product catalog, supplier directories, purchase order creation/receiving, and user role management.
- **`EMPLOYEE`**: Restricted access allowing product lookup, sales transactions, live inventory checks, and business dashboard analytics.

### 3. ⚡ Query Optimization & Indexing (Phase 16)
Engineered for scale with targeted B-Tree indexes on high-frequency query paths:
- `sales(sale_date)` & `sales(product_id)`: Accelerates 30-day velocity aggregations and reorder metrics.
- `products(category)` & `products(supplier_id)`: Optimizes category filtering and supplier foreign key joins.
- `purchase_orders(supplier_id)`: Speeds up supplier procurement lookups.

### 4. 🗄️ Database Migrations (Phase 17)
- Database schema changes are strictly version-controlled with **Alembic**, eliminating manual `ALTER TABLE` statements.

### 5. 🧪 Automated Testing Suite (Phase 15)
- **21 automated tests** covering:
  - Token validation & expired token handling
  - RBAC privilege enforcement
  - Input validation (negative prices, missing fields)
  - Atomic inventory decrement and stock deficit handling

---

## 📁 Repository Structure

```text
inventory_ai/
├── backend/
│   ├── app/
│   │   ├── core/                  # Security utilities & JWT token validation
│   │   ├── database/              # SQLAlchemy connection, models, indexes & clean scripts
│   │   ├── routes/                # REST endpoints (auth, products, inventory, sales, analytics, POs)
│   │   ├── schemas/               # Request validation schemas
│   │   └── main.py                # Flask application entry point
│   ├── alembic/                   # Database migration history
│   ├── tests/                     # Automated Pytest suite
│   ├── requirements.txt           # Python dependencies
│   └── .env                       # Environment configuration (git-ignored)
├── frontend/
│   ├── src/
│   │   ├── api/                   # Centralized Axios HTTP client
│   │   ├── components/            # Reusable UI widgets and navigation
│   │   ├── pages/                 # React views (Dashboard, Products, Sales, Inventory, etc.)
│   │   └── App.jsx                # Application root routing
│   ├── package.json               # Frontend dependencies & scripts
│   └── vite.config.js             # Vite development server config
├── API.md                         # Detailed REST API endpoint specification
└── README.md                      # Project documentation
```

---

## 🚀 Running the Project Locally

### Prerequisites
- Python 3.11+
- Node.js 18+
- MySQL Server 8.0+ running on `localhost:3306` with database `inventory_ai`

---

### 1. Backend Service
```powershell
# Navigate to the backend directory
cd "backend"

# Activate the virtual environment
.\venv\Scripts\Activate.ps1

# Run the Flask server
python -m app.main
```
> Serving on: **`http://127.0.0.1:8001`**

### 2. Frontend Application
```powershell
# In a new terminal, navigate to the frontend directory
cd "frontend"

# Start the Vite development server
npm run dev
```
> Running on: **`http://localhost:3000`**

### 3. Run Automated Tests
```powershell
cd "backend"
.\venv\Scripts\pytest.exe tests/ -v
```
All **21 test suites** will execute against the API client fixture with 100% pass rate.

---

## 📖 REST API Overview

See [**`API.md`**](API.md) for full request/response schemas.

| Method | Endpoint | Access | Description |
|---|---|---|---|
| `POST` | `/auth/login` | Public | Authenticates user and returns 24h JWT token |
| `GET` | `/products/` | Public | Lists active products with pagination & category filter |
| `POST` | `/products/` | `ADMIN` | Creates new catalog item |
| `POST` | `/sales/` | Authenticated | Records sale and atomically decrements inventory |
| `GET` | `/inventory/` | Authenticated | Live inventory levels and reorder warnings |
| `POST` | `/purchase-orders/` | `ADMIN` | Generates supplier procurement purchase order |
| `POST` | `/purchase-orders/<id>/receive` | `ADMIN` | Receives PO and restocks inventory units |
| `GET` | `/analytics/inventory-summary`| Authenticated | Real-time stock valuation and turnover KPIs |
