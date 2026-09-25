import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("shop.db")

def create_tables(connection: sqlite3.Connection) -> None:
    connection.executescript("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS customer_profiles (
            customer_id INTEGER PRIMARY KEY,
            phone TEXT,
            address TEXT,
            FOREIGN KEY (customer_id)
                REFERENCES customers(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price_cents INTEGER NOT NULL CHECK (price_cents >= 0),
            stock_quantity INTEGER NOT NULL DEFAULT 0
                CHECK (stock_quantity >= 0)
        );

        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            status TEXT NOT NULL DEFAULT 'new'
                CHECK (status IN ('new', 'paid', 'cancelled')),
            FOREIGN KEY (customer_id)
                REFERENCES customers(id) ON DELETE RESTRICT
        );

        CREATE TABLE IF NOT EXISTS order_items (
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL CHECK (quantity > 0),
            unit_price_cents INTEGER NOT NULL
                CHECK (unit_price_cents >= 0),
            PRIMARY KEY (order_id, product_id),
            FOREIGN KEY (order_id)
                REFERENCES orders(id) ON DELETE CASCADE,
            FOREIGN KEY (product_id)
                REFERENCES products(id) ON DELETE RESTRICT
        );

        CREATE INDEX IF NOT EXISTS idx_orders_customer_id
            ON orders(customer_id);
    """)


def seed_data(connection: sqlite3.Connection) -> None:
    count = connection.execute(
        "SELECT COUNT(*) FROM customers"
    ).fetchone()[0]

    if count != 0:
        return

    with connection:
        connection.executemany(
            "INSERT INTO customers (id, full_name, email) VALUES (?, ?, ?)",
            [
                (1, "Іван Петренко", "ivan@example.com"),
                (2, "Олена Коваль", "olena@example.com"),
            ],
        )

        connection.executemany(
            """
            INSERT INTO customer_profiles
                (customer_id, phone, address)
            VALUES (?, ?, ?)
            """,
            [
                (1, "+380501112233", "Київ, вул. Хрещатик, 1"),
                (2, "+380671234567", "Львів, вул. Городоцька, 10"),
            ],
        )

        connection.executemany(
            """
            INSERT INTO products
                (id, name, price_cents, stock_quantity)
            VALUES (?, ?, ?, ?)
            """,
            [
                (1, "Клавіатура", 250000, 10),
                (2, "Миша", 120000, 20),
                (3, "Монітор", 890000, 5),
            ],
        )

        connection.executemany(
            "INSERT INTO orders (id, customer_id, status) VALUES (?, ?, ?)",
            [
                (1, 1, "paid"),
                (2, 1, "new"),
                (3, 2, "new"),
            ],
        )

        connection.executemany(
            """
            INSERT INTO order_items
                (order_id, product_id, quantity, unit_price_cents)
            VALUES (?, ?, ?, ?)
            """,
            [
                (1, 1, 1, 250000),
                (1, 2, 2, 120000),
                (2, 3, 1, 890000),
                (3, 2, 1, 120000),
            ],
        )


def initialize_database() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.row_factory = sqlite3.Row

    try:
        create_tables(connection)
        seed_data(connection)
    except Exception:
        connection.close()
        raise

    return connection