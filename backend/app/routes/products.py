from flask import Blueprint, jsonify, request

from app.database.connection import SessionLocal
from app.database.models import Product

from app.routes.auth import token_required, admin_required
import logging

logger = logging.getLogger(__name__)

products_bp = Blueprint(
    "products",
    __name__,
    url_prefix="/products"
)


# ---------------------------------------------------------
# GET ALL PRODUCTS
# ---------------------------------------------------------
@products_bp.route("/", methods=["GET"])
def get_products():

    db = SessionLocal()

    try:
        query = db.query(Product).filter(Product.is_active == True)

        search = request.args.get('search')
        if search:
            query = query.filter(Product.name.ilike(f"%{search}%"))

        category = request.args.get('category')
        if category:
            query = query.filter(Product.category == category)

        supplier_id = request.args.get('supplier_id', type=int)
        if supplier_id:
            query = query.filter(Product.supplier_id == supplier_id)

        sort_by = request.args.get('sort_by', default='id')
        order = request.args.get('order', default='asc')

        sort_column_map = {
            'id': Product.id,
            'name': Product.name,
            'price': Product.price,
            'category': Product.category
        }
        sort_column = sort_column_map.get(sort_by, Product.id)

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
        products = query.offset((page - 1) * limit).limit(limit).all()

        result = []
        for product in products:
            result.append({
                "id": product.id,
                "name": product.name,
                "category": product.category,
                "price": float(product.price),
                "supplier_id": product.supplier_id
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
        logger.error(f"Failed to fetch products: {e}")
        return jsonify({
            "success": False,
            "message": "An internal error occurred. Please try again later."
        }), 500

    finally:
        db.close()


# ---------------------------------------------------------
# GET SINGLE PRODUCT
# ---------------------------------------------------------
@products_bp.route("/<int:product_id>", methods=["GET"])
def get_product(product_id):

    db = SessionLocal()

    try:
        product = db.query(Product).filter(
            Product.id == product_id,
            Product.is_active == True
        ).first()

        if product is None:
            return jsonify({
                "success": False,
                "message": "Product not found"
            }), 404

        return jsonify({
            "success": True,
            "data": {
                "id": product.id,
                "name": product.name,
                "category": product.category,
                "price": float(product.price),
                "supplier_id": product.supplier_id
            }
        }), 200

    except Exception as e:
        logger.error(f"Failed to fetch product {product_id}: {e}")
        return jsonify({
            "success": False,
            "message": "An internal error occurred. Please try again later."
        }), 500

    finally:
        db.close()


# ---------------------------------------------------------
# ---------------------------------------------------------
# CREATE PRODUCT
# ---------------------------------------------------------
@products_bp.route("/", methods=["POST"])
@token_required
@admin_required
def create_product():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Request body is required"
        }), 400

    required_fields = [
        "name",
        "category",
        "price",
        "supplier_id"
    ]

    for field in required_fields:

        if field not in data:
            return jsonify({
                "success": False,
                "message": f"{field} is required"
            }), 400

    try:
        price = float(data["price"])
    except (ValueError, TypeError):
        return jsonify({"success": False, "message": "price must be a valid number"}), 400

    if price <= 0:
        return jsonify({"success": False, "message": "price must be greater than 0"}), 400

    try:
        supplier_id = int(data["supplier_id"])
    except (ValueError, TypeError):
        return jsonify({"success": False, "message": "supplier_id must be a valid integer"}), 400

    db = SessionLocal()

    try:
        from app.database.models import Supplier

        supplier = db.query(Supplier).filter(
            Supplier.id == supplier_id,
            Supplier.is_active == True
        ).first()

        if not supplier:
            return jsonify({"success": False, "message": "Supplier not found"}), 404

        new_product = Product(
            name=data["name"],
            category=data["category"],
            price=price,
            supplier_id=supplier_id,
            is_active=True
        )

        db.add(new_product)
        db.commit()
        db.refresh(new_product)

        logger.info(f"Product created: id={new_product.id}, name={new_product.name}")

        return jsonify({
            "success": True,
            "message": "Product created successfully",
            "data": {
                "id": new_product.id,
                "name": new_product.name,
                "category": new_product.category,
                "price": float(new_product.price),
                "supplier_id": new_product.supplier_id
            }
        }), 201

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create product: {e}")
        return jsonify({
            "success": False,
            "message": "An internal error occurred. Please try again later."
        }), 500

    finally:
        db.close()


# ---------------------------------------------------------
# UPDATE PRODUCT
# ---------------------------------------------------------
@products_bp.route("/<int:product_id>", methods=["PUT"])
@token_required
@admin_required
def update_product(product_id):

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Request body is required"
        }), 400

    db = SessionLocal()

    try:
        from app.database.models import Supplier

        product = db.query(Product).filter(
            Product.id == product_id,
            Product.is_active == True
        ).first()

        if product is None:
            return jsonify({
                "success": False,
                "message": "Product not found"
            }), 404

        if "name" in data:
            product.name = data["name"]

        if "category" in data:
            product.category = data["category"]

        if "price" in data:
            try:
                price = float(data["price"])
            except (ValueError, TypeError):
                return jsonify({"success": False, "message": "price must be a valid number"}), 400

            if price <= 0:
                return jsonify({"success": False, "message": "price must be greater than 0"}), 400

            product.price = price

        if "supplier_id" in data:
            try:
                supplier_id = int(data["supplier_id"])
            except (ValueError, TypeError):
                return jsonify({"success": False, "message": "supplier_id must be a valid integer"}), 400

            supplier = db.query(Supplier).filter(
                Supplier.id == supplier_id,
                Supplier.is_active == True
            ).first()

            if not supplier:
                return jsonify({"success": False, "message": "Supplier not found"}), 404

            product.supplier_id = supplier_id

        db.commit()
        db.refresh(product)

        logger.info(f"Product updated: id={product.id}")

        return jsonify({
            "success": True,
            "message": "Product updated successfully",
            "data": {
                "id": product.id,
                "name": product.name,
                "category": product.category,
                "price": float(product.price),
                "supplier_id": product.supplier_id
            }
        }), 200

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update product {product_id}: {e}")
        return jsonify({
            "success": False,
            "message": "An internal error occurred. Please try again later."
        }), 500

    finally:
        db.close()


# ---------------------------------------------------------
# SOFT DELETE PRODUCT
# ---------------------------------------------------------
@products_bp.route("/<int:product_id>", methods=["DELETE"])
@token_required
@admin_required
def delete_product(product_id):

    db = SessionLocal()

    try:

        product = db.query(Product).filter(
            Product.id == product_id,
            Product.is_active == True
        ).first()

        if product is None:
            return jsonify({
                "success": False,
                "message": "Product not found"
            }), 404

        product.is_active = False

        db.commit()

        logger.info(f"Product deactivated: id={product.id}")

        return jsonify({
            "success": True,
            "message": "Product deactivated successfully"
        }), 200

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to deactivate product {product_id}: {e}")
        return jsonify({
            "success": False,
            "message": "An internal error occurred. Please try again later."
        }), 500

    finally:
        db.close()