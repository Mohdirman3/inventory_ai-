from flask import Blueprint, request, jsonify
from app.database.connection import SessionLocal
from app.database.models import Inventory, Product
from app.routes.auth import token_required, admin_required
import logging
logger = logging.getLogger(__name__)
inventory_bp = Blueprint('inventory', __name__)


@inventory_bp.route('/inventory/', methods=['GET'])
def get_all_inventory():
    db = SessionLocal()
    try:
        inventory_records = db.query(Inventory).all()

        result = []
        for record in inventory_records:
            result.append({
                "id": record.id,
                "product_id": record.product_id,
                "product_name": record.product.name if record.product else None,
                "quantity": record.quantity,
                "last_updated": record.last_updated.isoformat() if record.last_updated else None
            })

        return jsonify({"success": True, "data": result}), 200

    except Exception as e:
        logger.error(f"Failed to fetch inventory: {e}")
        return jsonify({"success": False, "message": "An internal error occurred. Please try again later."}), 500

    finally:
        db.close()


@inventory_bp.route('/inventory/low-stock', methods=['GET'])
def get_low_stock():
    db = SessionLocal()
    try:
        threshold = request.args.get('threshold', default=10, type=int)

        low_stock_records = db.query(Inventory).filter(Inventory.quantity <= threshold).all()

        result = []
        for record in low_stock_records:
            result.append({
                "product_id": record.product_id,
                "product_name": record.product.name if record.product else None,
                "quantity": record.quantity
            })

        return jsonify({
            "success": True,
            "threshold": threshold,
            "count": len(result),
            "data": result
        }), 200

    except Exception as e:
        logger.error(f"Failed to fetch low-stock inventory: {e}")
        return jsonify({"success": False, "message": "An internal error occurred. Please try again later."}), 500

    finally:
        db.close()


@inventory_bp.route('/inventory/<int:product_id>', methods=['GET'])
def get_inventory_by_product(product_id):
    db = SessionLocal()
    try:
        record = db.query(Inventory).filter(Inventory.product_id == product_id).first()

        if not record:
            return jsonify({"success": False, "message": "No inventory record found for this product"}), 404

        return jsonify({
            "success": True,
            "data": {
                "id": record.id,
                "product_id": record.product_id,
                "product_name": record.product.name if record.product else None,
                "quantity": record.quantity,
                "last_updated": record.last_updated.isoformat() if record.last_updated else None
            }
        }), 200

    except Exception as e:
        logger.error(f"Failed to fetch inventory for product {product_id}: {e}")
        return jsonify({"success": False, "message": "An internal error occurred. Please try again later."}), 500

    finally:
        db.close()


@inventory_bp.route('/inventory/', methods=['POST'])
@token_required
@admin_required
def create_inventory():
    db = SessionLocal()
    try:
        data = request.get_json()

        product_id = data.get('product_id')
        quantity = data.get('quantity')

        if product_id is None or quantity is None:
            return jsonify({"success": False, "message": "product_id and quantity are required"}), 400

        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return jsonify({"success": False, "message": "Product not found"}), 404

        existing = db.query(Inventory).filter(Inventory.product_id == product_id).first()
        if existing:
            return jsonify({"success": False, "message": "Inventory record already exists for this product"}), 400

        if quantity < 0:
            return jsonify({"success": False, "message": "Quantity cannot be negative"}), 400

        new_record = Inventory(product_id=product_id, quantity=quantity)
        db.add(new_record)
        db.commit()
        db.refresh(new_record)

        logger.info(f"Inventory record created: product_id={new_record.product_id}, quantity={new_record.quantity}")

        return jsonify({
            "success": True,
            "message": "Inventory record created successfully",
            "data": {
                "id": new_record.id,
                "product_id": new_record.product_id,
                "quantity": new_record.quantity
            }
        }), 201

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create inventory record: {e}")
        return jsonify({"success": False, "message": "An internal error occurred. Please try again later."}), 500

    finally:
        db.close()


@inventory_bp.route('/inventory/<int:product_id>', methods=['PUT'])
@token_required
@admin_required
def update_inventory(product_id):
    db = SessionLocal()
    try:
        data = request.get_json()
        quantity = data.get('quantity')

        record = db.query(Inventory).filter(Inventory.product_id == product_id).first()

        if not record:
            return jsonify({"success": False, "message": "No inventory record found for this product"}), 404

        if quantity is None:
            return jsonify({"success": False, "message": "quantity is required"}), 400

        if quantity < 0:
            return jsonify({"success": False, "message": "Quantity cannot be negative"}), 400

        record.quantity = quantity
        db.commit()
        db.refresh(record)

        logger.info(f"Inventory updated: product_id={record.product_id}, quantity={record.quantity}")

        return jsonify({
            "success": True,
            "message": "Inventory updated successfully",
            "data": {
                "id": record.id,
                "product_id": record.product_id,
                "quantity": record.quantity,
                "last_updated": record.last_updated.isoformat() if record.last_updated else None
            }
        }), 200

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update inventory for product {product_id}: {e}")
        return jsonify({"success": False, "message": "An internal error occurred. Please try again later."}), 500

    finally:
        db.close()


@inventory_bp.route('/inventory/<int:product_id>/add', methods=['POST'])
@token_required
@admin_required
def add_stock(product_id):
    db = SessionLocal()
    try:
        data = request.get_json()
        amount = data.get('quantity')

        if amount is None:
            return jsonify({"success": False, "message": "quantity is required"}), 400

        if amount <= 0:
            return jsonify({"success": False, "message": "quantity to add must be positive"}), 400

        record = db.query(Inventory).filter(Inventory.product_id == product_id).first()

        if not record:
            return jsonify({"success": False, "message": "No inventory record found for this product"}), 404

        record.quantity += amount
        db.commit()
        db.refresh(record)

        logger.info(f"Stock added: product_id={product_id}, amount={amount}, new_quantity={record.quantity}")

        return jsonify({
            "success": True,
            "message": f"Added {amount} units",
            "data": {
                "product_id": record.product_id,
                "new_quantity": record.quantity
            }
        }), 200

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to add stock for product {product_id}: {e}")
        return jsonify({"success": False, "message": "An internal error occurred. Please try again later."}), 500

    finally:
        db.close()


@inventory_bp.route('/inventory/<int:product_id>/remove', methods=['POST'])
@token_required
@admin_required
def remove_stock(product_id):
    db = SessionLocal()
    try:
        data = request.get_json()
        amount = data.get('quantity')

        if amount is None:
            return jsonify({"success": False, "message": "quantity is required"}), 400

        if amount <= 0:
            return jsonify({"success": False, "message": "quantity to remove must be positive"}), 400

        record = db.query(Inventory).filter(Inventory.product_id == product_id).first()

        if not record:
            return jsonify({"success": False, "message": "No inventory record found for this product"}), 404

        if amount > record.quantity:
            return jsonify({
                "success": False,
                "message": f"Cannot remove {amount} units — only {record.quantity} in stock"
            }), 400

        record.quantity -= amount
        db.commit()
        db.refresh(record)

        logger.info(f"Stock removed: product_id={product_id}, amount={amount}, new_quantity={record.quantity}")

        return jsonify({
            "success": True,
            "message": f"Removed {amount} units",
            "data": {
                "product_id": record.product_id,
                "new_quantity": record.quantity
            }
        }), 200

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to remove stock for product {product_id}: {e}")
        return jsonify({"success": False, "message": "An internal error occurred. Please try again later."}), 500

    finally:
        db.close()