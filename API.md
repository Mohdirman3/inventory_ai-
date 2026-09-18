# Inventory AI — REST API Documentation

Comprehensive reference documentation for the **Inventory AI REST API**.

- **Base URL**: `http://127.0.0.1:8001`
- **Default Content-Type**: `application/json`
- **Standard Response Shape**:
  ```json
  {
    "success": true,
    "message": "Human readable status message",
    "data": { ... }
  }
  ```

---

## 🔐 Authentication & Roles

The API uses JSON Web Tokens (JWT) signed with `HS256`. Tokens expire after **24 hours**.

Pass the token in the HTTP `Authorization` header for protected endpoints:
```http
Authorization: Bearer <your_jwt_token>
```

### Role-Based Access Control (RBAC):
- **`ADMIN`**: Full permissions across all resources (create, update, soft-delete, receive orders, view metrics).
- **`EMPLOYEE`**: Can view resources, record sales, adjust inventory, and view analytics. Restricted from creating/editing products and suppliers.

---

## 1. Authentication Routes (`/auth`)

### 1.1 Register User
- **Endpoint**: `POST /auth/register`
- **Access**: Public
- **Request Body**:
  ```json
  {
    "name": "Alex Johnson",
    "email": "alex@company.com",
    "password": "SecurePassword123",
    "role": "EMPLOYEE"
  }
  ```
  *(Role defaults to `EMPLOYEE`. Allowed values: `ADMIN`, `EMPLOYEE`)*
- **Response** (`201 Created`):
  ```json
  {
    "success": true,
    "message": "User registered successfully",
    "data": {
      "id": 1,
      "name": "Alex Johnson",
      "email": "alex@company.com",
      "role": "EMPLOYEE"
    }
  }
  ```

### 1.2 Login
- **Endpoint**: `POST /auth/login`
- **Access**: Public
- **Request Body**:
  ```json
  {
    "email": "alex@company.com",
    "password": "SecurePassword123"
  }
  ```
- **Response** (`200 OK`):
  ```json
  {
    "success": true,
    "message": "Login successful",
    "data": {
      "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "user": {
        "id": 1,
        "name": "Alex Johnson",
        "email": "alex@company.com",
        "role": "EMPLOYEE"
      }
    }
  }
  ```

### 1.3 Team Summary
- **Endpoint**: `GET /auth/team-summary`
- **Access**: `@token_required`, `@admin_required`
- **Response** (`200 OK`):
  ```json
  {
    "success": true,
    "data": {
      "total_users": 5,
      "total_admins": 2,
      "total_employees": 3
    }
  }
  ```

### 1.4 Update Profile
- **Endpoint**: `PUT /auth/profile`
- **Access**: `@token_required`
- **Request Body**:
  ```json
  {
    "name": "Alex J.",
    "email": "alex.new@company.com"
  }
  ```

### 1.5 Change Password
- **Endpoint**: `PUT /auth/change-password`
- **Access**: `@token_required`
- **Request Body**:
  ```json
  {
    "current_password": "OldPassword123",
    "new_password": "NewSecurePassword456"
  }
  ```

---

## 2. Products Routes (`/products`)

### 2.1 List Products
- **Endpoint**: `GET /products/`
- **Access**: Public
- **Query Parameters**:
  | Parameter | Type | Default | Description |
  |---|---|---|---|
  | `search` | string | `null` | Filters by name (case-insensitive substring) |
  | `category` | string | `null` | Exact category match |
  | `supplier_id`| integer | `null` | Filter by supplier ID |
  | `sort_by` | string | `id` | Sort column (`id`, `name`, `price`, `category`) |
  | `order` | string | `asc` | Sort direction (`asc`, `desc`) |
  | `page` | integer | `1` | Page number |
  | `limit` | integer | `10` | Records per page (1 to 100) |
- **Response** (`200 OK`):
  ```json
  {
    "success": true,
    "data": [
      {
        "id": 1,
        "name": "Wireless Ergonomic Mouse",
        "category": "Electronics",
        "price": 49.99,
        "supplier_id": 2
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 45,
      "total_pages": 5
    }
  }
  ```

### 2.2 Get Product By ID
- **Endpoint**: `GET /products/<int:product_id>`
- **Access**: Public

### 2.3 Create Product
- **Endpoint**: `POST /products/`
- **Access**: `@token_required`, `@admin_required`
- **Request Body**:
  ```json
  {
    "name": "Mechanical Gaming Keyboard",
    "category": "Electronics",
    "price": 89.99,
    "supplier_id": 1
  }
  ```
- **Response** (`201 Created`)

### 2.4 Update Product
- **Endpoint**: `PUT /products/<int:product_id>`
- **Access**: `@token_required`, `@admin_required`

### 2.5 Delete Product (Soft Delete)
- **Endpoint**: `DELETE /products/<int:product_id>`
- **Access**: `@token_required`, `@admin_required`
- **Behavior**: Sets `is_active = False` to preserve historical sales integrity.

---

## 3. Suppliers Routes (`/suppliers`)

### 3.1 List Suppliers
- **Endpoint**: `GET /suppliers/`
- **Access**: Public
- **Query Parameters**: `search`, `sort_by`, `order`, `page`, `limit`

### 3.2 Create Supplier
- **Endpoint**: `POST /suppliers/`
- **Access**: `@token_required`, `@admin_required`
- **Request Body**:
  ```json
  {
    "name": "Global Tech Distributors",
    "email": "orders@globaltech.com",
    "phone": "+1-555-0199",
    "lead_time_days": 5
  }
  ```

### 3.3 Delete Supplier (Soft Delete)
- **Endpoint**: `DELETE /suppliers/<int:supplier_id>`
- **Access**: `@token_required`, `@admin_required`
- **Constraint**: Rejects deletion (`400 Bad Request`) if active products are still mapped to this supplier.

---

## 4. Inventory Routes (`/inventory`)

### 4.1 Get Stock Levels
- **Endpoint**: `GET /inventory/`
- **Access**: `@token_required`

### 4.2 Set Stock Count (Manual Audit)
- **Endpoint**: `PUT /inventory/<int:product_id>`
- **Access**: `@token_required`
- **Request Body**: `{"quantity": 50}`

### 4.3 Add Stock
- **Endpoint**: `POST /inventory/<int:product_id>/add`
- **Access**: `@token_required`
- **Request Body**: `{"quantity": 25}`

### 4.4 Remove Stock
- **Endpoint**: `POST /inventory/<int:product_id>/remove`
- **Access**: `@token_required`
- **Request Body**: `{"quantity": 10}`
- **Constraint**: Blocks removal if quantity exceeds current stock (cannot drop below 0).

### 4.5 Low Stock Alert
- **Endpoint**: `GET /inventory/low-stock?threshold=10`
- **Access**: `@token_required`

---

## 5. Sales Routes (`/sales`)

### 5.1 List Sales
- **Endpoint**: `GET /sales/`
- **Access**: `@token_required`

### 5.2 Record Sale (Atomic Transaction)
- **Endpoint**: `POST /sales/`
- **Access**: `@token_required`
- **Request Body**:
  ```json
  {
    "product_id": 1,
    "quantity": 2
  }
  ```
- **Behavior**:
  1. Checks active product existence.
  2. Verifies `inventory.quantity >= quantity`.
  3. Inserts `Sale` record.
  4. Decrements `inventory.quantity`.
  5. Commits inside a single atomic transaction (rolls back if either step fails).
- **Response** (`201 Created`):
  ```json
  {
    "success": true,
    "message": "Sale recorded successfully",
    "data": {
      "id": 104,
      "product_id": 1,
      "product_name": "Mechanical Gaming Keyboard",
      "quantity": 2,
      "total_amount": 179.98,
      "sale_date": "2026-09-18T18:00:00.000Z",
      "remaining_stock": 48
    }
  }
  ```

---

## 6. Purchase Orders Routes (`/purchase-orders`)

### 6.1 List Purchase Orders
- **Endpoint**: `GET /purchase-orders/`
- **Access**: `@token_required`
- **Response**: Returns list of orders with populated supplier info and line items.

### 6.2 Create Purchase Order
- **Endpoint**: `POST /purchase-orders/`
- **Access**: `@token_required`, `@admin_required`
- **Request Body**:
  ```json
  {
    "supplier_id": 1,
    "items": [
      {
        "product_id": 1,
        "quantity": 50,
        "unit_price": 45.00
      },
      {
        "product_id": 3,
        "quantity": 20,
        "unit_price": 18.50
      }
    ]
  }
  ```

### 6.3 Mark Order Received (Atomic Stock Increment)
- **Endpoint**: `PUT /purchase-orders/<int:order_id>/receive`
- **Access**: `@token_required`
- **Behavior**: Sets order status to `RECEIVED` and increments stock for each line item within a single database transaction. Prevents double-receiving.

---

## 7. Analytics Routes (`/analytics`)

### 7.1 Inventory Summary
- **Endpoint**: `GET /analytics/inventory-summary`
- **Access**: `@token_required`
- **Response**:
  ```json
  {
    "success": true,
    "data": {
      "total_active_products": 42,
      "total_stock_units": 1580,
      "low_stock_products": 4,
      "out_of_stock_products": 1
    }
  }
  ```

### 7.2 Top Selling Products
- **Endpoint**: `GET /analytics/top-selling`
- **Access**: `@token_required`
- **Response**: Top 5 best-selling products grouped by total quantity sold.

### 7.3 Smart Reorder Recommendations
- **Endpoint**: `GET /analytics/reorder-recommendations`
- **Access**: `@token_required`
- **Algorithm**:
  $$\text{Daily Sales Rate} = \frac{\text{Sales in last 30 days}}{30}$$
  $$\text{Lead Time Demand} = \text{Daily Sales Rate} \times \text{Supplier Lead Time (Days)}$$
  Flags `REORDER` if:
  $$\text{Current Stock} \le \text{Lead Time Demand}$$
- **Response**:
  ```json
  {
    "success": true,
    "count": 1,
    "data": [
      {
        "product_id": 4,
        "product_name": "USB-C Fast Charger",
        "current_stock": 8,
        "avg_daily_sales": 2.4,
        "supplier_lead_time_days": 5,
        "projected_need_during_lead_time": 12.0,
        "recommendation": "REORDER"
      }
    ]
  }
  ```

### 7.4 Supplier Performance
- **Endpoint**: `GET /analytics/supplier-performance`
- **Access**: `@token_required`
- **Response**: Summary of total purchase orders, fulfillment rate (`RECEIVED` vs `PENDING`/`CANCELLED`), and lead times per supplier.
