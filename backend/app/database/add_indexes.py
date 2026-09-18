"""
Database Indexing Script for Inventory AI (Phase 16)
Adds indexes to frequently queried columns to optimize query performance.
"""

import logging
from sqlalchemy import text
from app.database.connection import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("db_indexer")

INDEXES = [
    ("idx_products_category", "products", "category"),
    ("idx_products_supplier_id", "products", "supplier_id"),
    ("idx_sales_product_id", "sales", "product_id"),
    ("idx_sales_sale_date", "sales", "sale_date"),
    ("idx_purchase_orders_supplier_id", "purchase_orders", "supplier_id"),
    ("idx_po_items_po_id", "purchase_order_items", "purchase_order_id"),
    ("idx_po_items_product_id", "purchase_order_items", "product_id"),
]


def apply_indexes():
    logger.info("Applying database indexes for query optimization...")

    with engine.connect() as conn:
        for idx_name, table_name, column_name in INDEXES:
            try:
                # Check if index already exists
                check_sql = text(f"SHOW INDEX FROM {table_name} WHERE Key_name = :idx_name")
                result = conn.execute(check_sql, {"idx_name": idx_name}).fetchall()

                if result:
                    logger.info(f"[-] Index '{idx_name}' on `{table_name}`(`{column_name}`) already exists.")
                else:
                    create_sql = text(f"CREATE INDEX {idx_name} ON {table_name}({column_name})")
                    conn.execute(create_sql)
                    conn.commit()
                    logger.info(f"[+] Successfully created index '{idx_name}' on `{table_name}`(`{column_name}`).")

            except Exception as e:
                logger.error(f"[!] Error handling index '{idx_name}' on `{table_name}`: {e}")

    logger.info("Database optimization complete!")


if __name__ == "__main__":
    apply_indexes()
