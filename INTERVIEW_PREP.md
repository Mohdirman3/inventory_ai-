# 🎯 Inventory AI — Comprehensive Interview Preparation & Demo Guide

Master reference for technical interviews, system design explanations, and live recruiter/interviewer demos.

---

## ⚡ 1. The 30-Second Elevator Pitch
> *"I built **Inventory AI**, a full-stack enterprise inventory tracking and replenishment platform using Python Flask, React, and MySQL. It solves the classic stock-out and phantom inventory problem by using ACID transactions to atomically deduct stock during sales and replenish items on purchase order receipts. I designed it with JWT-based Role-Based Access Control to separate Admin and Employee workflows, added targeted B-Tree indexes on high-velocity query columns like sale dates and foreign keys, automated schema migrations with Alembic, and backed the entire backend with 21 automated Pytest integration tests."*

---

## 💡 2. Guaranteed Technical Questions & Model Answers

### Q1: Why Flask over Django or FastAPI?
**Answer:**
> *"I chose Flask for its micro-framework flexibility and lightweight footprint. Because this system is centered on custom business logic (atomic sales deduction and role-based permissions), Flask gave me full control over the application lifecycle and middleware without Django’s opinionated ORM and admin overhead. For high-speed CRUD with SQLAlchemy 2.0 and Blueprint modularity, Flask strikes the sweet spot between simplicity and maintainability."*

### Q2: Explain your Database Schema and Relationships.
**Answer:**
> *"The schema consists of 6 primary relational models connected via SQLAlchemy:
> 1. **`User`**: Manages credentials and roles (`ADMIN` vs `EMPLOYEE`).
> 2. **`Supplier`**: One-to-many relationship with `Product` and `PurchaseOrder`.
> 3. **`Product`**: Central catalog item. One-to-one with `Inventory`, one-to-many with `Sale` and `PurchaseOrderItem`. Has a soft-delete flag `is_active`.
> 4. **`Inventory`**: Stores current available stock count, safety buffer, and last updated timestamps.
> 5. **`Sale`**: Records point-of-sale transactions and total revenue with indexed `sale_date`.
> 6. **`PurchaseOrder` & `PurchaseOrderItem`**: Handles multi-line item procurement from vendors."*

### Q3: What is a Database Transaction, and where did you use it?
**Answer:**
> *"A database transaction enforces ACID properties (Atomicity, Consistency, Isolation, Durability) ensuring all steps succeed or none do.
> In my app, the critical transaction is inside **`POST /sales/`**:
> 1. We query current stock for the item.
> 2. We verify `inventory.quantity >= quantity`.
> 3. We create the `Sale` record.
> 4. We decrement `inventory.quantity -= quantity`.
> 5. We execute `db.commit()`.
> If anything fails halfway (e.g. server crash or validation error), `db.rollback()` executes, guaranteeing inventory is never reduced without a corresponding sale record, preventing phantom stock."*

### Q4: How does Authentication & Authorization work?
**Answer:**
> - **Authentication (Who are you?)**: The user sends email and password to `POST /auth/login`. Passwords are verified against salted hashes using `werkzeug.security`. Upon success, we issue a stateless JSON Web Token (JWT) signed with `HS256` that expires after 24 hours.
> - **Authorization (What are you allowed to do?)**: We implemented custom Python decorators:
>   - `@token_required`: Decodes and verifies the JWT signature and expiration.
>   - `@admin_required`: Inspects the payload's `role` claim. If an `EMPLOYEE` attempts an admin-only route (like creating products or receiving POs), the API rejects with HTTP `403 Forbidden`."*

### Q5: How do you prevent SQL Injection?
**Answer:**
> *"We use **SQLAlchemy 2.0 ORM** and parameterized queries. SQLAlchemy abstracts SQL generation and binds user input as parameters rather than string concatenation. Even when raw SQL was needed for index inspection in `add_indexes.py`, we used `text()` with named bind parameters `:idx_name`."*

### Q6: Why Soft Delete (`is_active = False`) instead of Hard Delete?
**Answer:**
> *"Hard-deleting a product from the database triggers foreign key constraint failures on historical `sales` and `purchase_order_items` tables, destroying sales reports and auditing trails. Soft deleting preserves historical revenue records and turnover analytics while filtering deleted items out of live storefronts and active order forms."*

### Q7: Why and where did you add Database Indexes? (Phase 16)
**Answer:**
> *"Without indexes, queries perform full table scans ($O(N)$). I analyzed our slowest query paths:
> - `sales.sale_date`: Aggregating rolling 30-day velocity for reorder alerts requires filtering by date. Indexing it turns a full scan into an index range scan ($O(\log N)$).
> - `sales.product_id` and `products.supplier_id`: Frequently used in `JOIN` conditions.
> - `products.category`: Frequently filtered in product catalog views.
> I applied these via SQLAlchemy model definitions (`index=True`) and verified them with a migration script."*

### Q8: Tell me about a bug you debugged.
**Answer:**
> *"During testing, we noticed that if a user attempted to purchase an item with insufficient inventory, a partial record or an uncaught 500 error could occur. I isolated the issue, added an explicit check before stock deduction, and wrote integration tests in Pytest (`test_sale_fails_on_insufficient_stock` and `test_sale_decrements_inventory_atomically`). Now, attempts to sell more than available quantity immediately return a clean 400 Bad Request without touching the database session."*

### Q9: How would you scale this system 100x?
**Answer:**
> 1. **Caching**: Introduce Redis to cache frequent read-heavy responses like `/products/` and category lists with TTL-based invalidation.
> 2. **Database Replication**: Separate MySQL into a primary read-write instance and multiple read-replicas for analytics and reporting queries.
> 3. **Asynchronous Tasks**: Offload heavy reporting, email alerts, and supplier notifications to Celery or RQ workers backed by Redis.
> 4. **Horizontal Scaling**: Containerize backend with Docker, run behind Gunicorn / Nginx, and scale across container pods via Kubernetes or AWS ECS."*

### Q10: What are the current weaknesses, and what would you do differently? (Phase 21.5)
**Answer:**
> *"I believe in honest engineering self-awareness:
> 1. Currently, test runs execute against the local MySQL instance; in enterprise CI/CD, I'd spin up an isolated SQLite in-memory DB or Dockerized test container.
> 2. Token blacklisting/revocation: If an employee is revoked, their JWT remains valid until the 24-hour expiration unless we store a revocation blocklist in Redis.
> 3. Add automated optimistic locking (`version_id`) on the `Inventory` table to handle high-concurrency race conditions during flash sales."*

---

## 🎬 3. Bulletproof Live Demo Walkthrough Script (Phase 21.3)

Follow this exact 5-minute sequence when presenting to an interviewer:

```text
[Step 1: Introduction]
"Let's look at the live application. Here is the dashboard displaying real-time metrics."
-> Point to: Total Products, Low Stock Warnings, and Revenue Trends.

[Step 2: Role-Based Access Control]
"First, I'll demonstrate authorization."
-> Show logged in as Imran (ADMIN). Show the 'Add Product' and 'Purchase Orders' buttons are enabled.

[Step 3: Atomic Transaction - The Sale]
"Now let's verify our ACID transaction logic."
-> Go to 'Products' or 'Inventory'. Note the stock of "Joystick" (e.g. 25 units).
-> Go to 'Sales', record a sale for 5 units of "Joystick".
-> Immediately show 'Inventory': stock dropped to 20 units.
-> Try selling 1000 units: system instantly blocks it with "Insufficient stock".

[Step 4: Restocking via Purchase Orders]
"When stock runs low, we generate a vendor PO."
-> Go to 'Purchase Orders', create a new PO for 10 units with status PENDING.
-> Click "Receive Order": order switches to RECEIVED, and stock on Inventory increases by 10 automatically.

[Step 5: Code Quality & Automated Tests]
"Finally, every single critical path is backed by automated tests."
-> Switch to terminal and run: python -m pytest tests/ -v
-> Show all 21 tests passing in under half a second.
```
