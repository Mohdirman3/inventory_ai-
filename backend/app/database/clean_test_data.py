"""
Clean up test data and standardize database records for Inventory AI.
Phase 20 - Final Audit & Polish
"""

import logging
from app.database.connection import SessionLocal
from app.database.models import Product, Supplier, Inventory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("db_cleaner")


def clean_database():
    db = SessionLocal()
    try:
        logger.info("Starting database cleanup...")

        # 1. Clean up 'Test Product 99'
        test_product = db.query(Product).filter(Product.name == "Test Product 99").first()
        if test_product:
            # Remove associated inventory record first
            db.query(Inventory).filter(Inventory.product_id == test_product.id).delete()
            db.delete(test_product)
            logger.info(f"[+] Removed test product: 'Test Product 99' (ID: {test_product.id})")
        else:
            logger.info("[-] 'Test Product 99' not found.")

        # 2. Fix trailing whitespace in product names (e.g. 'Laptop ')
        trailing_products = db.query(Product).filter(Product.name.like("% ")).all()
        for prod in trailing_products:
            original = prod.name
            prod.name = prod.name.strip()
            logger.info(f"[+] Trimmed product name: '{original}' -> '{prod.name}'")

        # 3. Clean up test suppliers ('Bad Email Test', 'Test Supplier 9')
        test_suppliers = db.query(Supplier).filter(
            Supplier.name.in_(["Bad Email Test", "Test Supplier 9"])
        ).all()
        for sup in test_suppliers:
            sup_name = sup.name
            db.delete(sup)
            logger.info(f"[+] Removed test supplier: '{sup_name}' (ID: {sup.id})")

        db.commit()
        logger.info("Database cleanup completed successfully!")

    except Exception as e:
        db.rollback()
        logger.error(f"[!] Error cleaning database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    clean_database()
