from decimal import Decimal
from repository import ShopRepository

class ShopInfoService:
    def __init__(self, repository: ShopRepository):
        self.repository = repository

    def print_report(self) -> None:
        products = {
            product.id: product
            for product in self.repository.get_products()
        }

        for customer in self.repository.get_customers():
            print(f"\nПокупець: {customer.full_name}")
            print(f"Email: {customer.email}")

            profile = self.repository.get_profile(customer.id)
            if profile is not None:
                print(f"Телефон: {profile.phone or 'не вказано'}")
                print(f"Адреса: {profile.address or 'не вказано'}")

            orders = self.repository.get_orders_by_customer(customer.id)

            if not orders:
                print("Замовлень немає.")
                continue

            for order in orders:
                print(
                    f"\n  Замовлення №{order.id} | "
                    f"дата: {order.created_at} | "
                    f"статус: {order.status}"
                )

                total = Decimal("0.00")

                for item in self.repository.get_order_items(order.id):
                    product = products[item.product_id]
                    subtotal = item.unit_price * item.quantity
                    total += subtotal

                    print(
                        f"    {product.name}: {item.quantity} шт. × "
                        f"{item.unit_price:.2f} грн = "
                        f"{subtotal:.2f} грн"
                    )

                print(f"  Разом: {total:.2f} грн")