import json


def test_get_products_public(client):
    """GET /products/ is public and should return pagination structure."""
    response = client.get("/products/")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert "data" in data
    assert "pagination" in data
    assert data["pagination"]["page"] == 1


def test_get_nonexistent_product(client):
    """GET /products/<id> for a non-existent ID should return 404."""
    response = client.get("/products/99999999")
    assert response.status_code == 404
    data = response.get_json()
    assert data["success"] is False
    assert "Product not found" in data["message"]


def test_create_product_unauthorized(client):
    """Creating a product without a token should return 401."""
    payload = {
        "name": "Unauthorized Test Product",
        "category": "Electronics",
        "price": 99.99,
        "supplier_id": 1
    }
    response = client.post(
        "/products/",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code == 401
    data = response.get_json()
    assert data["success"] is False
    assert "Token is missing" in data["message"]


def test_create_product_forbidden_for_employee(client, employee_headers):
    """Creating a product as an EMPLOYEE should return 403."""
    payload = {
        "name": "Employee Test Product",
        "category": "Electronics",
        "price": 49.99,
        "supplier_id": 1
    }
    response = client.post(
        "/products/",
        data=json.dumps(payload),
        headers=employee_headers
    )
    assert response.status_code == 403
    data = response.get_json()
    assert data["success"] is False
    assert "Admin access required" in data["message"]


def test_create_product_missing_fields(client, admin_headers):
    """Creating a product with missing required fields should return 400."""
    payload = {
        "name": "Incomplete Product"
        # missing category, price, supplier_id
    }
    response = client.post(
        "/products/",
        data=json.dumps(payload),
        headers=admin_headers
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
    assert "required" in data["message"]


def test_create_product_invalid_price(client, admin_headers):
    """Creating a product with a negative or zero price should return 400."""
    payload = {
        "name": "Zero Price Product",
        "category": "Hardware",
        "price": -10.00,
        "supplier_id": 1
    }
    response = client.post(
        "/products/",
        data=json.dumps(payload),
        headers=admin_headers
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
    assert "greater than 0" in data["message"]


def test_create_product_nonexistent_supplier(client, admin_headers):
    """Creating a product with a supplier ID that doesn't exist should return 404."""
    payload = {
        "name": "No Supplier Product",
        "category": "Hardware",
        "price": 25.50,
        "supplier_id": 99999999
    }
    response = client.post(
        "/products/",
        data=json.dumps(payload),
        headers=admin_headers
    )
    assert response.status_code == 404
    data = response.get_json()
    assert data["success"] is False
    assert "Supplier not found" in data["message"]
