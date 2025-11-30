from sqlalchemy import (create_engine, Column, Integer, String, Float, DateTime,
                        ForeignKey, Boolean)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

DATABASE_URL = "sqlite:///supermarket.db"
engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, future=True)
Base = declarative_base()


class Store(Base):
    __tablename__ = "stores"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    city = Column(String, nullable=True)
    active = Column(Boolean, default=True)
    orders = relationship("Order", back_populates="store")


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    sku = Column(String, unique=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, index=True)
    price = Column(Float, nullable=False)          # preço de venda
    cost = Column(Float, nullable=True)            # custo opcional p/ margem
    stock = Column(Integer, default=0)
    order_items = relationship("OrderItem", back_populates="product")


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    created_at = Column(DateTime, nullable=False)
    customer_id = Column(String, nullable=True)    # se houver CRM
    store = relationship("Store", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")


def init_db():
    Base.metadata.create_all(bind=engine)
