from flask import Blueprint, request, jsonify
from app.database.connection import SessionLocal
from app.database.models import PurchaseOrder, PurchaseOrderItem, Supplier, Product, Inventory
from app.routes.auth import token_required, admin_required
from datetime import datetime, timezone
import logging
logger = logging.getLogger(__name__)
purchase_orders_bp = Blueprint('purchase_orders', __name__)


@purchase_orders_bp.route('/purchase-orders/', methods=['POST'])
@token_required
@admin_required
def create_purchase_order():
    db = SessionLocal()
    try:
        data = request.get_json()

        supplier_id = data.get('supplier_id')
        items = data.get('items')

        if supplier_id is None or not items:
            return jsonify({"success": False, "message": "supplier_id and items are required"}), 400

        supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
        if not supplier:
            return jsonify({"success": False, "message": "Supplier not found"}), 404

        for item in items:
            product_id = item.get('product_id')
            quantity = item.get('quantity')
            unit_price = item.get('unit_price')

            if product_id is None or quantity is None or unit_price is None:
                return jsonify({"success": False, "message": "Each item needs product_id, quantity, unit_price"}), 400

            if quantity <= 0 or unit_price < 0:
                return jsonify({"success": False, "message": "Invalid quantity or unit_price"}), 400

            product = db.query(Product).filter(Product.id == product_id, Product.is_active == True).first()
            if not product:
                return jsonify({"success": False, "message": f"Product {product_id} not found"}), 404

        new_order = PurchaseOrder(
            supplier_id=supplier_id,
            order_date=datetime.now(timezone.utc),
            status="PENDING"
        )
        db.add(new_order)
        db.flush()

        for item in items:
            order_item = PurchaseOrderItem(
                purchase_order_id=new_order.id,
                product_id=item['product_id'],
                quantity=item['quantity'],
                unit_price=item['unit_price']
            )
            db.add(order_item)

        db.commit()
        db.refresh(new_order)

        logger.info(f"Purchase order created: id={new_order.id}, supplier_id={supplier_id}")

        return jsonify({
            "success": True,
            "message": "Purchase order created successfully",
            "data": {
                "id": new_order.id,
                "supplier_id": new_order.supplier_id,
                "status": new_order.status,
                "order_date": new_order.order_date.isoformat(),
                "items": items
            }
        }), 201

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create purchase order: {e}")
        return jsonify({"success": False, "message": "An internal error occurred. Please try again later."}), 500

    finally:
        db.close()


@purchase_orders_bp.route('/purchase-orders/', methods=['GET'])
def get_all_purchase_orders():
    db = SessionLocal()
    try:
        orders = db.query(PurchaseOrder).all()

        result = []
        for order in orders:
            items = db.query(PurchaseOrderItem).filter(PurchaseOrderItem.purchase_order_id == order.id).all()
            result.append({
                "id": order.id,
                "supplier_id": order.supplier_id,
                "status": order.status,
                "order_date": order.order_date.isoformat() if order.order_date else None,
                "items": [
                    {
                        "product_id": item.product_id,
                        "quantity": item.quantity,
                        "unit_price": item.unit_price
                    } for item in items
                ]
            })

        return jsonify({"success": True, "data": result}), 200

    except Exception as e:
        logger.error(f"Failed to fetch purchase orders: {e}")
        return jsonify({"success": False, "message": "An internal error occurred. Please try again later."}), 500

    finally:
        db.close()


@purchase_orders_bp.route('/purchase-orders/<int:order_id>', methods=['GET'])
def get_purchase_order(order_id):
    db = SessionLocal()
    try:
        order = db.query(PurchaseOrder).filter(PurchaseOrder.id == order_id).first()

        if not order:
            return jsonify({"success": False, "message": "Purchase order not found"}), 404

        items = db.query(PurchaseOrderItem).filter(PurchaseOrderItem.purchase_order_id == order.id).all()

        return jsonify({
            "success": True,
            "data": {
                "id": order.id,
                "supplier_id": order.supplier_id,
                "status": order.status,
                "order_date": order.order_date.isoformat() if order.order_date else None,
                "items": [
                    {
                        "product_id": item.product_id,
                        "quantity": item.quantity,
                        "unit_price": item.unit_price
                    } for item in items
                ]
            }
        }), 200

    except Exception as e:
        logger.error(f"Failed to fetch purchase order {order_id}: {e}")
        return jsonify({"success": False, "message": "An internal error occurred. Please try again later."}), 500

    finally:
        db.close()


@purchase_orders_bp.route('/purchase-orders/<int:order_id>/receive', methods=['POST'])
@token_required
@admin_required
def receive_purchase_order(order_id):
    db = SessionLocal()
    try:
        order = db.query(PurchaseOrder).filter(PurchaseOrder.id == order_id).first()

        if not order:
            return jsonify({"success": False, "message": "Purchase order not found"}), 404

        if order.status == "RECEIVED":
            return jsonify({"success": False, "message": "Purchase order already received"}), 400

        if order.status == "CANCELLED":
            return jsonify({"success": False, "message": "Cannot receive a cancelled order"}), 400

        items = db.query(PurchaseOrderItem).filter(PurchaseOrderItem.purchase_order_id == order.id).all()

        if not items:
            return jsonify({"success": False, "message": "Purchase order has no items"}), 400

        for item in items:
            inventory = db.query(Inventory).filter(Inventory.product_id == item.product_id).first()

            if not inventory:
                inventory = Inventory(product_id=item.product_id, quantity=0)
                db.add(inventory)
                db.flush()

            inventory.quantity += item.quantity

        order.status = "RECEIVED"

        db.commit()
        db.refresh(order)

        logger.info(f"Purchase order received: id={order.id}, items={len(items)}")

        return jsonify({
            "success": True,
            "message": "Purchase order received — inventory updated",
            "data": {
                "id": order.id,
                "status": order.status
            }
        }), 200

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to receive purchase order {order_id}: {e}")
        return jsonify({"success": False, "message": "An internal error occurred. Please try again later."}), 500

    finally:
        db.close()