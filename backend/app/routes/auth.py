from flask import Blueprint, request, jsonify
from app.database.connection import SessionLocal
from app.database.models import User
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import jwt
import datetime
import os
from dotenv import load_dotenv
import logging
from pathlib import Path

env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY not found in .env file — check the file exists and is loaded correctly")


@auth_bp.route('/auth/register', methods=['POST'])
def register():
    db = SessionLocal()
    try:
        data = request.get_json()

        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'EMPLOYEE')

        if not name or not email or not password:
            return jsonify({"success": False, "message": "name, email, and password are required"}), 400

        if role not in ('ADMIN', 'EMPLOYEE'):
            return jsonify({"success": False, "message": "role must be ADMIN or EMPLOYEE"}), 400

        existing = db.query(User).filter(User.email == email).first()
        if existing:
            return jsonify({"success": False, "message": "Email already registered"}), 400

        password_hash = generate_password_hash(password)

        new_user = User(
            name=name,
            email=email,
            password_hash=password_hash,
            role=role
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        logger.info(f"User registered: id={new_user.id}, email={new_user.email}, role={new_user.role}")

        return jsonify({
            "success": True,
            "message": "User registered successfully",
            "data": {
                "id": new_user.id,
                "name": new_user.name,
                "email": new_user.email,
                "role": new_user.role
            }
        }), 201

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to register user: {e}")
        return jsonify({"success": False, "message": "An internal error occurred. Please try again later."}), 500

    finally:
        db.close()


@auth_bp.route('/auth/login', methods=['POST'])
def login():
    db = SessionLocal()
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"success": False, "message": "email and password are required"}), 400

        user = db.query(User).filter(User.email == email).first()

        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({"success": False, "message": "Invalid email or password"}), 401

        logger.info(f"User logged in: id={user.id}, email={user.email}")

        token = jwt.encode({
            "user_id": user.id,
            "role": user.role,
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
        }, SECRET_KEY, algorithm="HS256")

        return jsonify({
            "success": True,
            "message": "Login successful",
            "data": {
                "token": token,
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "role": user.role
                }
            }
        }), 200

    except Exception as e:
        logger.error(f"Failed to log in: {e}")
        return jsonify({"success": False, "message": "An internal error occurred. Please try again later."}), 500

    finally:
        db.close()


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')

        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

        if not token:
            return jsonify({"success": False, "message": "Token is missing"}), 401

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.user_id = payload['user_id']
            request.user_role = payload['role']
        except jwt.ExpiredSignatureError:
            return jsonify({"success": False, "message": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"success": False, "message": "Invalid token"}), 401

        return f(*args, **kwargs)

    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.user_role != 'ADMIN':
            return jsonify({"success": False, "message": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated

@auth_bp.route('/auth/team-summary', methods=['GET'])
@token_required
@admin_required
def team_summary():
    db = SessionLocal()
    try:
        total_users = db.query(User).count()
        total_admins = db.query(User).filter(User.role == 'ADMIN').count()
        total_employees = db.query(User).filter(User.role == 'EMPLOYEE').count()

        return jsonify({
            "success": True,
            "data": {
                "total_users": total_users,
                "total_admins": total_admins,
                "total_employees": total_employees
            }
        }), 200

    except Exception as e:
        logger.error(f"Failed to fetch team summary: {e}")
        return jsonify({"success": False, "message": "An internal error occurred. Please try again later."}), 500

    finally:
        db.close()
@auth_bp.route('/auth/profile', methods=['PUT'])
@token_required
def update_profile():
    db = SessionLocal()
    try:
        data = request.get_json()

        user = db.query(User).filter(User.id == request.user_id).first()

        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404

        if "name" in data:
            if not data["name"].strip():
                return jsonify({"success": False, "message": "Name cannot be empty"}), 400
            user.name = data["name"].strip()

        if "email" in data:
            new_email = data["email"].strip()
            if not new_email:
                return jsonify({"success": False, "message": "Email cannot be empty"}), 400

            existing = db.query(User).filter(
                User.email == new_email,
                User.id != user.id
            ).first()

            if existing:
                return jsonify({"success": False, "message": "That email is already in use"}), 409

            user.email = new_email

        db.commit()
        db.refresh(user)

        logger.info(f"Profile updated: user_id={user.id}")

        return jsonify({
            "success": True,
            "message": "Profile updated successfully",
            "data": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role
            }
        }), 200

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update profile: {e}")
        return jsonify({"success": False, "message": "An internal error occurred. Please try again later."}), 500

    finally:
        db.close()
@auth_bp.route('/auth/change-password', methods=['PUT'])
@token_required
def change_password():
    db = SessionLocal()
    try:
        data = request.get_json()

        current_password = data.get('current_password')
        new_password = data.get('new_password')

        if not current_password or not new_password:
            return jsonify({"success": False, "message": "current_password and new_password are required"}), 400

        if len(new_password) < 6:
            return jsonify({"success": False, "message": "New password must be at least 6 characters"}), 400

        user = db.query(User).filter(User.id == request.user_id).first()

        if not user or not check_password_hash(user.password_hash, current_password):
            return jsonify({"success": False, "message": "Current password is incorrect"}), 401

        user.password_hash = generate_password_hash(new_password)
        db.commit()

        logger.info(f"Password changed: user_id={user.id}")

        return jsonify({"success": True, "message": "Password changed successfully"}), 200

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to change password: {e}")
        return jsonify({"success": False, "message": "An internal error occurred. Please try again later."}), 500

    finally:
        db.close()