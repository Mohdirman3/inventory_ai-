import re
import logging
logger = logging.getLogger(__name__)
from flask import Blueprint, jsonify, request

from app.database.connection import SessionLocal
from app.database.models import Supplier
from app.routes.auth import token_required, admin_required

suppliers_bp = Blueprint(
    "suppliers",
    __name__,
    url_prefix="/suppliers"
)

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


# ---------------------------------------------------------
# GET ALL SUPPLIERS
# ---------------------------------------------------------
@suppliers_bp.route("/", methods=["GET"])
def get_suppliers():

    db = SessionLocal()

    try:
        query = db.query(Supplier).filter(Supplier.is_active == True)

        search = request.args.get('search')
        if search:
            query = query.filter(Supplier.name.ilike(f"%{search}%"))

        sort_by = request.args.get('sort_by', default='id')
        order = request.args.get('order', default='asc')

        sort_column_map = {
            'id': Supplier.id,
            'name': Supplier.name,
            'lead_time_days': Supplier.lead_time_days
        }
        sort_column = sort_column_map.get(sort_by, Supplier.id)

        if order == 'desc':
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        page = request.args.get('page', default=1, type=int)
        limit = request.args.get('limit', default=10, type=int)

        if page < 1:
            page = 1
        if limit < 1 or limit > 100:
            limit = 10

        total = query.count()
        suppliers = query.offset((page - 1) * limit).limit(limit).all()

        result = []
        for supplier in suppliers:
            result.append({
                "id": supplier.id,
                "name": supplier.name,
                "email": supplier.email,
                "phone": supplier.phone,
                "lead_time_days": supplier.lead_time_days
            })

        return jsonify({
            "success": True,
            "data": result,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": (total + limit - 1) // limit
            }
        }), 200

    except Exception as e:
        logger.error(f"Failed to fetch suppliers: {e}")
        return jsonify({
            "success": False,
            "message": "An internal error occurred. Please try again later."
        }), 500

    finally:
        db.close()


# ---------------------------------------------------------
# GET SINGLE SUPPLIER + PRODUCTS
# ---------------------------------------------------------
@suppliers_bp.route("/<int:supplier_id>", methods=["GET"])
def get_supplier(supplier_id):

    db = SessionLocal()

    try:
        supplier = db.query(Supplier).filter(
            Supplier.id == supplier_id
        ).first()

        if supplier is None:
            return jsonify({
                "success": False,
                "message": "Supplier not found"
            }), 404

        products = []

        for product in supplier.products:

            if product.is_active:
                products.append({
                    "id": product.id,
                    "name": product.name,
                    "category": product.category,
                    "price": float(product.price)
                })

        return jsonify({
            "success": True,
            "data": {
                "id": supplier.id,
                "name": supplier.name,
                "email": supplier.email,
                "phone": supplier.phone,
                "lead_time_days": supplier.lead_time_days,
                "products": products
            }
        }), 200

    except Exception as e:
        logger.error(f"Failed to fetch supplier {supplier_id}: {e}")
        return jsonify({
            "success": False,
            "message": "An internal error occurred. Please try again later."
        }), 500

    finally:
        db.close()


# ---------------------------------------------------------
# CREATE SUPPLIER
# ---------------------------------------------------------
@suppliers_bp.route("/", methods=["POST"])
@token_required
@admin_required
def create_supplier():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Request body is required"
        }), 400

    required_fields = [
        "name",
        "email",
        "phone",
        "lead_time_days"
    ]

    for field in required_fields:

        if field not in data:
            return jsonify({
                "success": False,
                "message": f"{field} is required"
            }), 400

    if not EMAIL_REGEX.match(data["email"]):
        return jsonify({"success": False, "message": "Invalid email format"}), 400

    try:
        lead_time_days = int(data["lead_time_days"])
    except (ValueError, TypeError):
        return jsonify({"success": False, "message": "lead_time_days must be a valid integer"}), 400

    if lead_time_days < 0:
        return jsonify({"success": False, "message": "lead_time_days cannot be negative"}), 400

    db = SessionLocal()

    try:

        existing_supplier = db.query(Supplier).filter(
            Supplier.email == data["email"]
        ).first()

        if existing_supplier:
            return jsonify({
                "success": False,
                "message": "Supplier with this email already exists"
            }), 409

        new_supplier = Supplier(
            name=data["name"],
            email=data["email"],
            phone=data["phone"],
            lead_time_days=lead_time_days
        )

        db.add(new_supplier)
        db.commit()
        db.refresh(new_supplier)

        logger.info(f"Supplier created: id={new_supplier.id}, name={new_supplier.name}")

        return jsonify({
            "success": True,
            "message": "Supplier created successfully",
            "data": {
                "id": new_supplier.id,
                "name": new_supplier.name,
                "email": new_supplier.email,
                "phone": new_supplier.phone,
                "lead_time_days": new_supplier.lead_time_days
            }
        }), 201

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create supplier: {e}")
        return jsonify({
            "success": False,
            "message": "An internal error occurred. Please try again later."
        }), 500

    finally:
        db.close()


# ---------------------------------------------------------
# UPDATE SUPPLIER
# ---------------------------------------------------------
@suppliers_bp.route("/<int:supplier_id>", methods=["PUT"])
@token_required
@admin_required
def update_supplier(supplier_id):

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Request body is required"
        }), 400

    db = SessionLocal()

    try:

        supplier = db.query(Supplier).filter(
            Supplier.id == supplier_id
        ).first()

        if supplier is None:
            return jsonify({
                "success": False,
                "message": "Supplier not found"
            }), 404

        if "name" in data:
            supplier.name = data["name"]

        if "email" in data:

            if not EMAIL_REGEX.match(data["email"]):
                return jsonify({"success": False, "message": "Invalid email format"}), 400

            existing_supplier = db.query(Supplier).filter(
                Supplier.email == data["email"],
                Supplier.id != supplier_id
            ).first()

            if existing_supplier:
                return jsonify({
                    "success": False,
                    "message": "Supplier with this email already exists"
                }), 409

            supplier.email = data["email"]

        if "phone" in data:
            supplier.phone = data["phone"]

        if "lead_time_days" in data:
            try:
                lead_time_days = int(data["lead_time_days"])
            except (ValueError, TypeError):
                return jsonify({"success": False, "message": "lead_time_days must be a valid integer"}), 400

            if lead_time_days < 0:
                return jsonify({"success": False, "message": "lead_time_days cannot be negative"}), 400

            supplier.lead_time_days = lead_time_days

        db.commit()
        db.refresh(supplier)

        logger.info(f"Supplier updated: id={supplier.id}")

        return jsonify({
            "success": True,
            "message": "Supplier updated successfully",
            "data": {
                "id": supplier.id,
                "name": supplier.name,
                "email": supplier.email,
                "phone": supplier.phone,
                "lead_time_days": supplier.lead_time_days
            }
        }), 200

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update supplier {supplier_id}: {e}")
        return jsonify({
            "success": False,
            "message": "An internal error occurred. Please try again later."
        }), 500

    finally:
        db.close()


# ---------------------------------------------------------
# SOFT DELETE SUPPLIER (foreign-key safe)
# ---------------------------------------------------------
@suppliers_bp.route("/<int:supplier_id>", methods=["DELETE"])
@token_required
@admin_required
def delete_supplier(supplier_id):

    db = SessionLocal()

    try:

        supplier = db.query(Supplier).filter(
            Supplier.id == supplier_id
        ).first()

        if supplier is None:
            return jsonify({
                "success": False,
                "message": "Supplier not found"
            }), 404

        active_products = [p for p in supplier.products if p.is_active]

        if active_products:
            return jsonify({
                "success": False,
                "message": f"Cannot delete supplier: {len(active_products)} active product(s) linked. Deactivate or reassign them first."
            }), 400

        supplier.is_active = False
        db.commit()

        logger.info(f"Supplier deactivated: id={supplier.id}")

        return jsonify({
            "success": True,
            "message": "Supplier deactivated successfully"
        }), 200

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to deactivate supplier {supplier_id}: {e}")
        return jsonify({
            "success": False,
            "message": "An internal error occurred. Please try again later."
        }), 500

    finally:
        db.close()