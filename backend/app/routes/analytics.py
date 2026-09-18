from flask import Blueprint, jsonify
from app.database.connection import SessionLocal
from app.database.models import Product, Inventory, Sale
from app.routes.auth import token_required
from sqlalchemy import func
from datetime import datetime, timedelta, timezone
import logging

logger = logging.getLogger(__name__)

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/analytics/inventory-summary', methods=['GET'])
@token_required
def inventory_summary():
    db = SessionLocal()
    try:
        total_products = db.query(Product).filter(Product.is_active == True).count()
        total_stock_units = int(db.query(func.sum(Inventory.quantity)).scalar() or 0)
        low_stock_count = db.query(Inventory).filter(Inventory.quantity <= 10).count()
        out_of_stock_count = db.query(Inventory).filter(Inventory.quantity == 0).count()
        return jsonify({
            "success": True,
            "data": {
                "total_active_products": total_products,
                "total_stock_units": total_stock_units,
                "low_stock_products": low_stock_count,
                "out_of_stock_products": out_of_stock_count
            }
        }), 200
    except Exception as e:
        logger.error(f"Failed to generate inventory summary: {e}")
        return jsonify({"success": False, "message": "An internal error occurred. Please try again later."}), 500
    finally:
        db.close()


@analytics_bp.route('/analytics/top-selling', methods=['GET'])
@token_required
def top_selling_products():
    db = SessionLocal()
    try:
        limit = 5

        results = (
            db.query(
                Product.id,
                Product.name,
                func.sum(Sale.quantity).label('total_sold')
            )
            .join(Sale, Sale.product_id == Product.id)
            .group_by(Product.id, Product.name)
            .order_by(func.sum(Sale.quantity).desc())
            .limit(limit)
            .all()
        )

        data = [
            {
                "product_id": r.id,
                "product_name": r.name,
                "total_sold": int(r.total_sold)
            }
            for r in results
        ]

        return jsonify({"success": True, "data": data}), 200

    except Exception as e:
        logger.error(f"Failed to generate top-selling report: {e}")
        return jsonify({"success": False, "message": "An internal error occurred. Please try again later."}), 500

    finally:
        db.close()


@analytics_bp.route('/analytics/reorder-recommendations', methods=['GET'])
@token_required
def reorder_recommendations():
    db = SessionLocal()
    try:
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)

        products = db.query(Product).filter(Product.is_active == True).all()

        recommendations = []

        for product in products:
            inventory = db.query(Inventory).filter(Inventory.product_id == product.id).first()
            current_stock = inventory.quantity if inventory else 0

            recent_sales = (
                db.query(func.sum(Sale.quantity))
                .filter(Sale.product_id == product.id, Sale.sale_date >= thirty_days_ago)
                .scalar() or 0
            )

            daily_sales_rate = recent_sales / 30

            supplier = product.supplier
            lead_time_days = supplier.lead_time_days if supplier else 7

            projected_need = daily_sales_rate * lead_time_days

            if daily_sales_rate > 0 and current_stock <= projected_need:
                recommendations.append({
                    "product_id": product.id,
                    "product_name": product.name,
                    "current_stock": current_stock,
                    "avg_daily_sales": round(daily_sales_rate, 2),
                    "supplier_lead_time_days": lead_time_days,
                    "projected_need_during_lead_time": round(projected_need, 2),
                    "recommendation": "REORDER"
                })

        return jsonify({
            "success": True,
            "count": len(recommendations),
            "data": recommendations
        }), 200

    except Exception as e:
        logger.error(f"Failed to generate reorder recommendations: {e}")
        return jsonify({"success": False, "message": "An internal error occurred. Please try again later."}), 500

    finally:
        db.close()

@analytics_bp.route('/analytics/supplier-performance', methods=['GET'])
@token_required
def supplier_performance():
    db = SessionLocal()
    try:
        from app.database.models import Supplier, PurchaseOrder

        suppliers = db.query(Supplier).filter(Supplier.is_active == True).all()

        result = []

        for supplier in suppliers:
            active_product_count = db.query(Product).filter(
                Product.supplier_id == supplier.id,
                Product.is_active == True
            ).count()

            total_orders = db.query(PurchaseOrder).filter(
                PurchaseOrder.supplier_id == supplier.id
            ).count()

            received_orders = db.query(PurchaseOrder).filter(
                PurchaseOrder.supplier_id == supplier.id,
                PurchaseOrder.status == "RECEIVED"
            ).count()

            fulfillment_rate = round((received_orders / total_orders * 100), 1) if total_orders > 0 else None

            result.append({
                "supplier_id": supplier.id,
                "supplier_name": supplier.name,
                "lead_time_days": supplier.lead_time_days,
                "active_products_supplied": active_product_count,
                "total_purchase_orders": total_orders,
                "received_orders": received_orders,
                "fulfillment_rate_percent": fulfillment_rate
            })

        result.sort(key=lambda s: s["lead_time_days"])

        return jsonify({"success": True, "data": result}), 200

    except Exception as e:
        logger.error(f"Failed to generate supplier performance report: {e}")
        return jsonify({"success": False, "message": "An internal error occurred. Please try again later."}), 500

    finally:
        db.close()