from database import initialize_database
from repository import ShopRepository
from service import ShopInfoService


def main() -> None:
    connection = initialize_database()

    try:
        repository = ShopRepository(connection)
        service = ShopInfoService(repository)
        service.print_report()
    finally:
        connection.close()


if __name__ == "__main__":
    main()