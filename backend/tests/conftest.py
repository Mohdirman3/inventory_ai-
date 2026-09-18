import pytest
import jwt
import datetime
import os
from app.main import create_app
from app.database.connection import SessionLocal
from app.routes.auth import SECRET_KEY


@pytest.fixture(scope="session")
def app():
    """Create Flask application instance for testing."""
    flask_app = create_app()
    flask_app.config.update({
        "TESTING": True,
    })
    return flask_app


@pytest.fixture
def client(app):
    """Test client for issuing HTTP requests."""
    return app.test_client()


@pytest.fixture
def db_session():
    """Database session fixture."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def admin_token():
    """Generate a valid JWT token for an ADMIN user."""
    payload = {
        "user_id": 999991,
        "role": "ADMIN",
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


@pytest.fixture
def employee_token():
    """Generate a valid JWT token for an EMPLOYEE user."""
    payload = {
        "user_id": 999992,
        "role": "EMPLOYEE",
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


@pytest.fixture
def admin_headers(admin_token):
    """Headers with Admin Authorization token."""
    return {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }


@pytest.fixture
def employee_headers(employee_token):
    """Headers with Employee Authorization token."""
    return {
        "Authorization": f"Bearer {employee_token}",
        "Content-Type": "application/json"
    }
