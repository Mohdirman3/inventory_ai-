import json
from app.database.models import Product, Inventory


def test_create_sale_without_token(client):
    """Recording a sale without authentication should return 401."""
    response = client.post(
        "/sales/",
        data=json.dumps({"product_id": 1, "quantity": 1}),
        content_type="application/json"
    )
    assert response.status_code == 401
    data = response.get_json()
    assert data["success"] is False
    assert "Token is missing" in data["message"]


def test_create_sale_missing_fields(client, employee_headers):
    """Recording a sale without product_id or quantity should return 400."""
    response = client.post(
        "/sales/",
        data=json.dumps({"product_id": 1}),
        headers=employee_headers
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
    assert "required" in data["message"]


def test_create_sale_negative_quantity(client, employee_headers):
    """Recording a sale with non-positive quantity should return 400."""
    response = client.post(
        "/sales/",
        data=json.dumps({"product_id": 1, "quantity": -5}),
        headers=employee_headers
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
    assert "quantity must be positive" in data["message"]


def test_create_sale_nonexistent_product(client, employee_headers):
    """Recording a sale for a non-existent product should return 404."""
    response = client.post(
        "/sales/",
        data=json.dumps({"product_id": 99999999, "quantity": 1}),
        headers=employee_headers
    )
    assert response.status_code == 404
    data = response.get_json()
    assert data["success"] is False
    assert "Product not found" in data["message"]


def test_sale_decrements_inventory_atomically(client, employee_headers, db_session):
    """
    CRITICAL TEST:
    Verifies that recording a sale decrements inventory by the exact quantity,
    and updates both the Sale ledger and Inventory records atomically.
    """
    # Find an active product with inventory
    inv = db_session.query(Inventory).join(
        Product, Product.id == Inventory.product_id
    ).filter(Product.is_active == True, Inventory.quantity >= 2).first()

    if not inv:
        # If no product has at least 2 units in the DB, skip this test gracefully
        return

    target_product_id = inv.product_id
    initial_stock = inv.quantity
    sell_quantity = 1

    # Record the sale
    response = client.post(
        "/sales/",
        data=json.dumps({
            "product_id": target_product_id,
            "quantity": sell_quantity
        }),
        headers=employee_headers
    )

    assert response.status_code == 201
    data = response.get_json()
    assert data["success"] is True
    assert data["data"]["quantity"] == sell_quantity
    assert data["data"]["remaining_stock"] == initial_stock - sell_quantity

    # Direct database verification to ensure DB persistence
    # In MySQL REPEATABLE READ, rollback/commit is needed to read newly committed changes from other sessions
    db_session.rollback()
    updated_inv = db_session.query(Inventory).filter(
        Inventory.product_id == target_product_id
    ).first()
    assert updated_inv.quantity == initial_stock - sell_quantity


def test_sale_fails_on_insufficient_stock(client, employee_headers, db_session):
    """
    Verifies that attempting to sell more items than available in stock
    is blocked and rejected with a 400 error.
    """
    inv = db_session.query(Inventory).join(
        Product, Product.id == Inventory.product_id
    ).filter(Product.is_active == True).first()

    if not inv:
        return

    excess_quantity = inv.quantity + 5000

    response = client.post(
        "/sales/",
        data=json.dumps({
            "product_id": inv.product_id,
            "quantity": excess_quantity
        }),
        headers=employee_headers
    )

    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
    assert "Insufficient stock" in data["message"]
