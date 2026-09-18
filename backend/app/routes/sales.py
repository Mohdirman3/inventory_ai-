import logging
logger = logging.getLogger(__name__)

from flask import Blueprint, request, jsonify
from app.database.connection import SessionLocal
from app.database.models import Sale, Product, Inventory
from app.routes.auth import token_required, admin_required
from datetime import datetime, timezone

sales_bp = Blueprint('sales', __name__)


@sales_bp.route('/sales/', methods=['POST'])
@token_required
def create_sale():
    db = SessionLocal()
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        quantity = data.get('quantity')

        if product_id is None or quantity is None:
            return jsonify({"success": False, "message": "product_id and quantity are required"}), 400

        if quantity <= 0:
            return jsonify({"success": False, "message": "quantity must be positive"}), 400

        product = db.query(Product).filter(Product.id == product_id, Product.is_active == True).first()
        if not product:
            return jsonify({"success": False, "message": "Product not found"}), 404

        inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
        if not inventory:
            return jsonify({"success": False, "message": "No inventory record for this product"}), 404

        if inventory.quantity < quantity:
            return jsonify({
                "success": False,
                "message": f"Insufficient stock — only {inventory.quantity} available"
            }), 400

        total_amount = product.price * quantity

        new_sale = Sale(
            product_id=product_id,
            quantity=quantity,
            sale_date=datetime.now(timezone.utc),
            total_amount=total_amount
        )
        db.add(new_sale)

        inventory.quantity -= quantity

        db.commit()
        db.refresh(new_sale)

        logger.info(f"Sale recorded: sale_id={new_sale.id}, product_id={product_id}, quantity={quantity}, total={total_amount}")

        return jsonify({
            "success": True,
            "message": "Sale recorded successfully",
            "data": {
                "id": new_sale.id,
                "product_id": new_sale.product_id,
                "product_name": product.name,
                "quantity": new_sale.quantity,
                "total_amount": new_sale.total_amount,
                "sale_date": new_sale.sale_date.isoformat(),
                "remaining_stock": inventory.quantity
            }
        }), 201

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create sale: {e}")
        return jsonify({"success": False, "message": "An internal error occurred. Please try again later."}), 500

    finally:
        db.close()


@sales_bp.route('/sales/', methods=['GET'])
def get_all_sales():
    db = SessionLocal()
    try:
        sales = db.query(Sale).all()

        result = []
        for sale in sales:
            result.append({
                "id": sale.id,
                "product_id": sale.product_id,
                "product_name": sale.product.name if sale.product else None,
                "quantity": sale.quantity,
                "total_amount": sale.total_amount,
                "sale_date": sale.sale_date.isoformat() if sale.sale_date else None
            })

        return jsonify({"success": True, "data": result}), 200

    except Exception as e:
        logger.error(f"Failed to fetch sales: {e}")
        return jsonify({"success": False, "message": "An internal error occurred. Please try again later."}), 500

    finally:
        db.close()


@sales_bp.route('/sales/<int:sale_id>', methods=['GET'])
def get_sale(sale_id):
    db = SessionLocal()
    try:
        sale = db.query(Sale).filter(Sale.id == sale_id).first()

        if not sale:
            return jsonify({"success": False, "message": "Sale not found"}), 404

        return jsonify({
            "success": True,
            "data": {
                "id": sale.id,
                "product_id": sale.product_id,
                "product_name": sale.product.name if sale.product else None,
                "quantity": sale.quantity,
                "total_amount": sale.total_amount,
                "sale_date": sale.sale_date.isoformat() if sale.sale_date else None
            }
        }), 200

    except Exception as e:
        logger.error(f"Failed to fetch sale {sale_id}: {e}")
        return jsonify({"success": False, "message": "An internal error occurred. Please try again later."}), 500

    finally:
        db.close()