from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation

@dataclass
class Product:
    product_id: int
    name: str
    price: Decimal
    quantity: int


@dataclass(frozen=True)
class Sale:
    sale_id: int
    product_name: str
    quantity: int
    unit_price: Decimal
    created_at: datetime

    @property
    def total(self) -> Decimal:
        return self.unit_price * self.quantity


class Shop:
    def __init__(self):
        self.products: dict[int, Product] = {}
        self.sales: list[Sale] = []
        self.next_product_id = 1

    def add_product(
        self,
        name: str,
        price: Decimal,
        quantity: int,
    ) -> Product:
        name = name.strip()

        if not name:
            raise ValueError("Назва товару не може бути порожньою.")

        if not price.is_finite() or price <= 0:
            raise ValueError("Ціна повинна бути додатним скінченним числом.")

        if price != price.quantize(Decimal("0.01")):
            raise ValueError("Ціна повинна містити не більше двох знаків після коми.")

        if quantity < 0:
            raise ValueError("Початкова кількість не може бути від'ємною.")

        product = Product(
            product_id=self.next_product_id,
            name=name,
            price=price,
            quantity=quantity,
        )

        self.products[product.product_id] = product
        self.next_product_id += 1
        return product

    def get_product(self, product_id: int) -> Product:
        if product_id not in self.products:
            raise ValueError("Товар із таким ID не знайдено.")

        return self.products[product_id]

    def restock(self, product_id: int, quantity: int) -> Product:
        if quantity <= 0:
            raise ValueError("Кількість надходження повинна бути більшою за нуль.")

        product = self.get_product(product_id)
        product.quantity += quantity
        return product

    def sell(self, product_id: int, quantity: int) -> Sale:
        if quantity <= 0:
            raise ValueError("Кількість для продажу повинна бути більшою за нуль.")

        product = self.get_product(product_id)

        if quantity > product.quantity:
            raise ValueError(
                f"Недостатньо товару. Доступно: {product.quantity} шт."
            )

        sale = Sale(
            sale_id=len(self.sales) + 1,
            product_name=product.name,
            quantity=quantity,
            unit_price=product.price,
            created_at=datetime.now(),
        )

        product.quantity -= quantity
        self.sales.append(sale)
        return sale


def read_int(prompt: str) -> int:
    try:
        return int(input(prompt))
    except ValueError:
        raise ValueError("Потрібно ввести ціле число.") from None


def read_price(prompt: str) -> Decimal:
    raw_value = input(prompt).strip().replace(",", ".")

    try:
        price = Decimal(raw_value)

        if not price.is_finite() or price <= 0:
            raise ValueError("Ціна повинна бути додатним скінченним числом.")

        if price != price.quantize(Decimal("0.01")):
            raise ValueError("Введіть ціну з точністю до копійок.")

        return price

    except InvalidOperation:
        raise ValueError("Некоректна ціна.") from None


def show_products(shop: Shop) -> None:
    if not shop.products:
        print("\nКаталог порожній.")
        return

    print("\nКАТАЛОГ ТОВАРІВ")
    print(f"{'ID':<5} {'Назва':<25} {'Ціна, грн':>12} {'Залишок':>10}")
    print("-" * 56)

    for product in shop.products.values():
        print(
            f"{product.product_id:<5} "
            f"{product.name:<25} "
            f"{product.price:>12.2f} "
            f"{product.quantity:>10}"
        )


def add_product_action(shop: Shop) -> None:
    name = input("Назва товару: ")
    price = read_price("Ціна, грн: ")
    quantity = read_int("Початкова кількість: ")

    product = shop.add_product(name, price, quantity)
    print(f"Товар додано. ID: {product.product_id}")


def restock_action(shop: Shop) -> None:
    show_products(shop)
    product_id = read_int("\nID товару: ")
    quantity = read_int("Кількість надходження: ")

    product = shop.restock(product_id, quantity)
    print(f"Залишок товару «{product.name}»: {product.quantity} шт.")


def print_receipt(sale: Sale) -> None:
    print("\n" + "=" * 36)
    print(f"ЧЕК №{sale.sale_id}")
    print(f"Дата: {sale.created_at:%d.%m.%Y %H:%M:%S}")
    print(f"Товар: {sale.product_name}")
    print(f"Кількість: {sale.quantity} шт.")
    print(f"Ціна: {sale.unit_price:.2f} грн")
    print(f"До сплати: {sale.total:.2f} грн")
    print("=" * 36)


def sell_action(shop: Shop) -> None:
    show_products(shop)
    product_id = read_int("\nID товару: ")
    quantity = read_int("Кількість для продажу: ")

    sale = shop.sell(product_id, quantity)
    print_receipt(sale)


def show_sales(shop: Shop) -> None:
    if not shop.sales:
        print("\nПродажів ще немає.")
        return

    print("\nІСТОРІЯ ПРОДАЖІВ")

    for sale in shop.sales:
        print(
            f"№{sale.sale_id} | "
            f"{sale.created_at:%d.%m.%Y %H:%M:%S} | "
            f"{sale.product_name} | "
            f"{sale.quantity} шт. | "
            f"{sale.total:.2f} грн"
        )

    revenue = sum((sale.total for sale in shop.sales), Decimal("0"))
    print(f"\nЗагальна виручка: {revenue:.2f} грн")


def role_menu(shop: Shop, role: str) -> None:
    if role == "admin":
        title = "АДМІНІСТРАТОР"
        actions = {
            "1": ("Переглянути товари", show_products),
            "2": ("Додати товар", add_product_action),
            "3": ("Поповнити залишок", restock_action),
        }
    else:
        title = "КАСИР"
        actions = {
            "1": ("Переглянути товари", show_products),
            "2": ("Оформити продаж", sell_action),
            "3": ("Переглянути історію продажів", show_sales),
        }

    while True:
        print(f"\n--- {title} ---")

        for number, (label, _) in actions.items():
            print(f"{number}. {label}")

        print("0. Повернутися до вибору ролі")
        choice = input("Ваш вибір: ").strip()

        if choice == "0":
            return

        if choice not in actions:
            print("Невідомий пункт меню.")
            continue

        _, action = actions[choice]

        try:
            action(shop)
        except (ValueError, InvalidOperation) as error:
            print(f"Помилка: {error}")


def main() -> None:
    shop = Shop()

    shop.add_product("Хліб", Decimal("30.00"), 20)
    shop.add_product("Молоко", Decimal("45.50"), 15)
    shop.add_product("Кава", Decimal("180.00"), 10)

    while True:
        print("\n СИСТЕМА АВТОМАТИЗАЦІЇ МАГАЗИНУ ")
        print("1. Адміністратор")
        print("2. Касир")
        print("0. Завершити програму")

        choice = input("Ваш вибір: ").strip()

        if choice == "1":
            role_menu(shop, "admin")
        elif choice == "2":
            role_menu(shop, "cashier")
        elif choice == "0":
            print("Роботу завершено.")
            break
        else:
            print("Невідомий пункт меню.")


if __name__ == "__main__":
    main()