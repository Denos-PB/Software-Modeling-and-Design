import sqlite3
from decimal import Decimal
from models import Customer, CustomerProfile, Order, OrderItem, Product

def cents_to_money(cents: int) -> Decimal:
    return Decimal(cents) / Decimal(100)

class ShopRepository:
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def get_customers(self) -> list[Customer]:
        rows = self.connection.execute(
            "SELECT id, full_name, email FROM customers ORDER BY id"
        ).fetchall()

        return [
            Customer(row["id"], row["full_name"], row["email"])
            for row in rows
        ]

    def get_profile(self, customer_id: int) -> CustomerProfile | None:
        row = self.connection.execute(
            """
            SELECT customer_id, phone, address
            FROM customer_profiles
            WHERE customer_id = ?
            """,
            (customer_id,),
        ).fetchone()

        if row is None:
            return None

        return CustomerProfile(
            row["customer_id"],
            row["phone"],
            row["address"],
        )

    def get_products(self) -> list[Product]:
        rows = self.connection.execute(
            """
            SELECT id, name, price_cents, stock_quantity
            FROM products
            ORDER BY id
            """
        ).fetchall()

        return [
            Product(
                row["id"],
                row["name"],
                cents_to_money(row["price_cents"]),
                row["stock_quantity"],
            )
            for row in rows
        ]

    def get_orders_by_customer(self, customer_id: int) -> list[Order]:
        rows = self.connection.execute(
            """
            SELECT id, customer_id, created_at, status
            FROM orders
            WHERE customer_id = ?
            ORDER BY id
            """,
            (customer_id,),
        ).fetchall()

        return [
            Order(
                row["id"],
                row["customer_id"],
                row["created_at"],
                row["status"],
            )
            for row in rows
        ]

    def get_order_items(self, order_id: int) -> list[OrderItem]:
        rows = self.connection.execute(
            """
            SELECT order_id, product_id, quantity, unit_price_cents
            FROM order_items
            WHERE order_id = ?
            ORDER BY product_id
            """,
            (order_id,),
        ).fetchall()

        return [
            OrderItem(
                row["order_id"],
                row["product_id"],
                row["quantity"],
                cents_to_money(row["unit_price_cents"]),
            )
            for row in rows
        ]