import json


def test_login_missing_fields(client):
    """Attempting login without email or password should return 400."""
    response = client.post(
        "/auth/login",
        data=json.dumps({}),
        content_type="application/json"
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
    assert "required" in data["message"]


def test_login_invalid_credentials(client):
    """Attempting login with nonexistent credentials should return 401."""
    response = client.post(
        "/auth/login",
        data=json.dumps({
            "email": "nonexistent_user_999999@test.com",
            "password": "WrongPassword123!"
        }),
        content_type="application/json"
    )
    assert response.status_code == 401
    data = response.get_json()
    assert data["success"] is False
    assert "Invalid email or password" in data["message"]


def test_register_missing_fields(client):
    """Attempting registration without required fields should return 400."""
    response = client.post(
        "/auth/register",
        data=json.dumps({"email": "test@example.com"}),
        content_type="application/json"
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False


def test_register_invalid_role(client):
    """Registration with an invalid role should be rejected."""
    response = client.post(
        "/auth/register",
        data=json.dumps({
            "name": "Test User",
            "email": "test_role_invalid@example.com",
            "password": "Password123",
            "role": "SUPERUSER"
        }),
        content_type="application/json"
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
    assert "role must be ADMIN or EMPLOYEE" in data["message"]


def test_protected_route_without_token(client):
    """Accessing a protected route without Authorization header should return 401."""
    response = client.get("/auth/team-summary")
    assert response.status_code == 401
    data = response.get_json()
    assert data["success"] is False
    assert "Token is missing" in data["message"]


def test_protected_route_with_invalid_token(client):
    """Accessing a protected route with an invalid token string should return 401."""
    headers = {"Authorization": "Bearer not_a_real_jwt_token"}
    response = client.get("/auth/team-summary", headers=headers)
    assert response.status_code == 401
    data = response.get_json()
    assert data["success"] is False
    assert "Invalid token" in data["message"]


def test_admin_route_forbidden_for_employee(client, employee_headers):
    """Employee tokens should receive 403 Forbidden on admin-only endpoints."""
    response = client.get("/auth/team-summary", headers=employee_headers)
    assert response.status_code == 403
    data = response.get_json()
    assert data["success"] is False
    assert "Admin access required" in data["message"]


def test_admin_route_allowed_for_admin(client, admin_headers):
    """Admin tokens should successfully access admin-only endpoints."""
    response = client.get("/auth/team-summary", headers=admin_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert "total_users" in data["data"]
