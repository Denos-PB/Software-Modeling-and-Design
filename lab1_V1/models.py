from dataclasses import dataclass
from decimal import Decimal

@dataclass
class Customer:
    id: int
    full_name: str
    email: str


@dataclass
class CustomerProfile:
    customer_id: int
    phone: str | None
    address: str | None


@dataclass
class Product:
    id: int
    name: str
    price: Decimal
    stock_quantity: int


@dataclass
class Order:
    id: int
    customer_id: int
    created_at: str
    status: str


@dataclass
class OrderItem:
    order_id: int
    product_id: int
    quantity: int
    unit_price: Decimal