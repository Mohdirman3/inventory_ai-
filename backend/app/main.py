from flask import Flask, jsonify
from flask_cors import CORS
from sqlalchemy import text


from app.routes.products import products_bp
from app.routes.suppliers import suppliers_bp
from app.routes.inventory import inventory_bp
from app.routes.sales import sales_bp
from app.routes.purchase_orders import purchase_orders_bp
from app.routes.auth import auth_bp
from app.routes.analytics import analytics_bp
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__)

    # Allow requests from React dev servers (localhost and 127.0.0.1 on ports 3000 and 5173)
    CORS(
        app,
        resources={r"/*": {"origins": [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:5173",
            "http://127.0.0.1:5173"
        ]}},
        supports_credentials=True
    )

    # Register API routes
    app.register_blueprint(products_bp)
    app.register_blueprint(suppliers_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(purchase_orders_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(analytics_bp)
    # Basic health-check endpoint
    @app.route("/", methods=["GET"])
    def home():
        logger.info("Home endpoint accessed")
        return {
            "message": "Inventory AI API is running"
        }

    # Database connection test
    @app.route("/db-test", methods=["GET"])
    def database_test():
        from app.database.connection import SessionLocal

        db = SessionLocal()

        try:
            db.execute(text("SELECT 1"))

            return {
                "database": "inventory_ai",
                "status": "connected"
            }

        except Exception as e:
            logger.error(f"DB connection test failed: {e}")
            return {
                "database": "inventory_ai",
                "status": "connection failed"
            }, 500

        finally:
            db.close()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=8001)