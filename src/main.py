"""Simple menu-driven demo for Group 3 Inventory Management System."""
from inventory import InventoryManager


def read_nonnegative_int(label: str) -> int:
    raw = input(label).strip()
    number = int(raw)
    if number < 0:
        raise ValueError("Value must not be negative")
    return number


def print_product(product) -> None:
    print(f"SKU: {product.sku} | Name: {product.name} | "
          f"Quantity: {product.quantity} | Min stock: {product.min_stock}")


def main() -> None:
    app = InventoryManager()
    print("=== Group 3 - Real-Time Inventory Management (Python PoC) ===")
    while True:
        print("\n1. Add product\n2. Find product by SKU\n3. Receive stock"
              "\n4. Sell stock\n5. Low-stock alerts\n6. Inventory report"
              "\n7. Transaction history\n8. Exit")
        choice = input("Select an option (1-8): ").strip()
        try:
            if choice == "1":
                product = app.add_product(
                    input("SKU: "), input("Product name: "),
                    read_nonnegative_int("Starting quantity: "),
                    read_nonnegative_int("Minimum stock threshold: "),
                )
                print("Added:")
                print_product(product)
            elif choice == "2":
                product = app.get_product(input("SKU: "))
                print_product(product) if product else print("Product not found")
            elif choice in ("3", "4"):
                sku = input("SKU: ")
                amount = read_nonnegative_int("Number of units: ")
                if amount == 0:
                    raise ValueError("Amount must be greater than zero")
                delta = amount if choice == "3" else -amount
                print_product(app.adjust_stock(sku, delta))
            elif choice == "5":
                records = app.low_stock_report()
                print(f"Low-stock products: {len(records)}")
                for product in records:
                    print_product(product)
            elif choice == "6":
                records = app.inventory_report()
                print(f"Total products: {len(records)}")
                for product in records:
                    print_product(product)
            elif choice == "7":
                records = app.transaction_history()
                print(f"Successful stock adjustments: {len(records)}")
                for record in records:
                    print(f"{record.timestamp_utc} | {record.sku} | "
                          f"change {record.change:+d} | {record.before} -> {record.after}")
            elif choice == "8":
                print("Goodbye!")
                break
            else:
                print("Please choose a number from 1 to 8")
        except (ValueError, KeyError) as exc:
            print(f"Error: {exc}")


if __name__ == "__main__":
    main()
