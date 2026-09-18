from sqlalchemy import (
    Boolean,
    DECIMAL,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import relationship

from app.database.connection import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
    )

    name = Column(
        String(150),
        nullable=False,
    )

    category = Column(
        String(100),
        nullable=False,
        index=True,
    )

    price = Column(
        DECIMAL(10, 2),
        nullable=False,
    )

    supplier_id = Column(
        Integer,
        ForeignKey("suppliers.id"),
        nullable=False,
        index=True,
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    supplier = relationship(
        "Supplier",
        back_populates="products",
    )

    inventory = relationship(
        "Inventory",
        back_populates="product",
        uselist=False,
    )

    sales = relationship(
        "Sale",
        back_populates="product",
    )

    purchase_order_items = relationship(
        "PurchaseOrderItem",
        back_populates="product",
    )

class Supplier(Base):
    __tablename__ = "suppliers"
    is_active = Column(Boolean, default=True)
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True)
    phone = Column(String(20))
    lead_time_days = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    products = relationship(
        "Product",
        back_populates="supplier",
    )
    purchase_orders = relationship(
        "PurchaseOrder",
        back_populates="supplier",
    )


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False,
        unique=True,
    )
    quantity = Column(Integer, nullable=False, default=0)
    last_updated = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )

    product = relationship("Product", back_populates="inventory")


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False,
        index=True,
    )
    quantity = Column(Integer, nullable=False)
    sale_date = Column(DateTime, nullable=False, index=True)
    total_amount = Column(DECIMAL(12, 2), nullable=False)

    product = relationship("Product", back_populates="sales")


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    supplier_id = Column(
        Integer,
        ForeignKey("suppliers.id"),
        nullable=False,
        index=True,
    )
    order_date = Column(DateTime, server_default=func.now())
    status = Column(String(20), nullable=False, default="PENDING")

    supplier = relationship(
        "Supplier",
        back_populates="purchase_orders",
    )
    items = relationship(
        "PurchaseOrderItem",
        back_populates="purchase_order",
    )


class PurchaseOrderItem(Base):
    __tablename__ = "purchase_order_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    purchase_order_id = Column(
        Integer,
        ForeignKey("purchase_orders.id"),
        nullable=False,
        index=True,
    )
    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False,
        index=True,
    )
    quantity = Column(Integer, nullable=False)
    unit_price = Column(DECIMAL(12, 2), nullable=False)

    purchase_order = relationship(
        "PurchaseOrder",
        back_populates="items",
    )
    product = relationship(
        "Product",
        back_populates="purchase_order_items",
    )

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="EMPLOYEE")
    created_at = Column(DateTime, server_default=func.now())
