"""Seven-feature Streamlit demo for the existing in-memory InventoryManager.

Run from this directory:
    python -m streamlit run app.py

The UI deliberately uses Streamlit columns instead of st.dataframe, so the
inventory tables do not need Pandas/NumPy to render.
"""

import csv
import io

import streamlit as st

from inventory import InventoryManager


st.set_page_config(page_title="Group 3 | Inventory Management", page_icon="📦", layout="wide")


def create_demo_inventory() -> InventoryManager:
    """Seed a few sample products so the seven features can be demonstrated."""
    store = InventoryManager()
    store.add_product("LAP-01", "Laptop", 10, 3)
    store.add_product("PHN-01", "Phone", 8, 4)
    store.add_product("KEY-01", "Keyboard", 15, 5)
    store.add_product("MOU-01", "Mouse", 2, 5)  # Example low-stock alert
    return store


if "inventory_manager" not in st.session_state:
    st.session_state.inventory_manager = create_demo_inventory()

store: InventoryManager = st.session_state.inventory_manager


FEATURES = [
    "1. Add Product",
    "2. Find Product by SKU",
    "3. Receive Stock",
    "4. Sell Stock",
    "5. Low-Stock Alerts",
    "6. Inventory Report",
    "7. Transaction History",
]


def csv_text(headers, rows):
    """Generate a CSV download without extra dependencies."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(headers)
    writer.writerows(rows)
    return buffer.getvalue()


def show_product_table(products):
    """Display products without st.dataframe (avoids Pandas import)."""
    if not products:
        st.info("No products to display.")
        return
    headings = st.columns([2, 3, 1, 1, 2])
    for column, heading in zip(headings, ["SKU", "Product", "Quantity", "Minimum", "Status"]):
        column.markdown(f"**{heading}**")
    st.divider()
    for product in products:
        cells = st.columns([2, 3, 1, 1, 2])
        cells[0].write(product.sku)
        cells[1].write(product.name)
        cells[2].write(str(product.quantity))
        cells[3].write(str(product.min_stock))
        cells[4].write("⚠️ Low stock" if product.quantity <= product.min_stock else "✅ In stock")


def show_transaction_table(transactions):
    """Display transaction history without a Pandas-based grid."""
    if not transactions:
        st.info("No transactions yet. Receive or sell stock to create one.")
        return
    headings = st.columns([3, 2, 1, 1, 1])
    for column, heading in zip(headings, ["Time (UTC)", "SKU", "Change", "Before", "After"]):
        column.markdown(f"**{heading}**")
    st.divider()
    for transaction in reversed(transactions):
        cells = st.columns([3, 2, 1, 1, 1])
        cells[0].write(transaction.timestamp_utc)
        cells[1].write(transaction.sku)
        cells[2].write(f"{transaction.change:+d}")
        cells[3].write(str(transaction.before))
        cells[4].write(str(transaction.after))


with st.sidebar:
    st.title("📦 Group 3")
    st.caption("Inventory Management Demo")
    selected_feature = st.radio("Choose a function", FEATURES, label_visibility="visible")
    st.divider()
    st.caption("The demo keeps data in memory for this session; it does not use a database.")
    if st.button("↻ Reset Demo Data", use_container_width=True):
        st.session_state.inventory_manager = create_demo_inventory()
        st.session_state.flash = "Demo data has been reset."
        st.rerun()

st.title("📦 Inventory Management System")
st.caption("Group 3 • Python / Streamlit • Seven inventory functions")

if "flash" in st.session_state:
    st.success(st.session_state.pop("flash"))

products = store.inventory_report()
low_stock_products = store.low_stock_report()
transactions = store.transaction_history()

metric1, metric2, metric3, metric4 = st.columns(4)
metric1.metric("Products", len(products))
metric2.metric("Total Units", sum(product.quantity for product in products))
metric3.metric("Low-Stock Alerts", len(low_stock_products))
metric4.metric("Transactions", len(transactions))
st.divider()


if selected_feature == "1. Add Product":
    st.subheader("1. Add Product")
    st.write("Register a product with a unique SKU, initial quantity, and minimum stock threshold.")
    with st.form("add_product", clear_on_submit=True):
        left, right = st.columns(2)
        with left:
            new_sku = st.text_input("Product SKU", placeholder="MON-01")
            new_quantity = st.number_input("Starting Quantity", min_value=0, step=1, value=10)
        with right:
            new_name = st.text_input("Product Name", placeholder="Monitor")
            new_minimum = st.number_input("Minimum Stock", min_value=0, step=1, value=3)
        submitted = st.form_submit_button("Add Product", type="primary")
    if submitted:
        try:
            product = store.add_product(new_sku, new_name, int(new_quantity), int(new_minimum))
        except ValueError as error:
            st.error(str(error))
        else:
            st.session_state.flash = f"Added {product.name} ({product.sku}) successfully."
            st.rerun()


elif selected_feature == "2. Find Product by SKU":
    st.subheader("2. Find Product by SKU")
    st.write("Enter the exact product SKU to find its information using dictionary lookup.")
    with st.form("find_product"):
        search_sku = st.text_input("SKU", placeholder="LAP-01")
        submitted = st.form_submit_button("Find Product", type="primary")
    if submitted:
        try:
            result = store.get_product(search_sku)
        except ValueError as error:
            st.error(str(error))
        else:
            if result is None:
                st.warning(f"No product found with SKU '{search_sku.strip()}'.")
            else:
                st.success(f"Found: {result.name}")
                show_product_table([result])


elif selected_feature == "3. Receive Stock":
    st.subheader("3. Receive Stock")
    st.write("Receive new units of an existing product (a positive stock adjustment).")
    if not products:
        st.info("Add a product first.")
    else:
        with st.form("receive_stock"):
            sku = st.selectbox(
                "Select Product",
                [p.sku for p in products],
                format_func=lambda value: f"{value} — {store.products[value].name} (available: {store.products[value].quantity})",
            )
            amount = st.number_input("Units Received", min_value=1, value=1, step=1)
            submitted = st.form_submit_button("Receive Stock", type="primary")
        if submitted:
            try:
                result = store.adjust_stock(sku, int(amount))
            except (ValueError, KeyError) as error:
                st.error(str(error))
            else:
                st.session_state.flash = f"Received {int(amount)} units of {result.name}. New quantity: {result.quantity}."
                st.rerun()


elif selected_feature == "4. Sell Stock":
    st.subheader("4. Sell Stock")
    st.write("Sell units from an existing product (a negative stock adjustment). Overselling is blocked.")
    if not products:
        st.info("Add a product first.")
    else:
        with st.form("sell_stock"):
            sku = st.selectbox(
                "Select Product",
                [p.sku for p in products],
                format_func=lambda value: f"{value} — {store.products[value].name} (available: {store.products[value].quantity})",
            )
            amount = st.number_input("Units to Sell", min_value=1, value=1, step=1)
            submitted = st.form_submit_button("Sell Stock", type="primary")
        if submitted:
            try:
                result = store.adjust_stock(sku, -int(amount))
            except (ValueError, KeyError) as error:
                st.error(str(error))
            else:
                st.session_state.flash = f"Sold {int(amount)} units of {result.name}. New quantity: {result.quantity}."
                st.rerun()


elif selected_feature == "5. Low-Stock Alerts":
    st.subheader("5. Low-Stock Alerts")
    st.write("A product is low on stock when its quantity is less than or equal to its minimum.")
    if low_stock_products:
        st.warning(f"⚠️ {len(low_stock_products)} product(s) need restocking.")
        show_product_table(low_stock_products)
    else:
        st.success("All products are above their minimum stock thresholds.")


elif selected_feature == "6. Inventory Report":
    st.subheader("6. Inventory Report")
    st.write("All products, sorted by SKU.")
    show_product_table(products)
    st.download_button(
        "Download Inventory Report (CSV)",
        data=csv_text(
            ["SKU", "Product", "Quantity", "Minimum Stock", "Status"],
            [
                [p.sku, p.name, p.quantity, p.min_stock, "Low stock" if p.quantity <= p.min_stock else "In stock"]
                for p in products
            ],
        ),
        file_name="inventory_report.csv",
        mime="text/csv",
    )


elif selected_feature == "7. Transaction History":
    st.subheader("7. Transaction History")
    st.write("Only successful stock adjustments appear here; adding a product does not create a transaction.")
    options = ["All products"] + [p.sku for p in products]
    history_sku = st.selectbox("Filter by SKU", options)
    filtered = store.transaction_history(None if history_sku == "All products" else history_sku)
    show_transaction_table(filtered)
    st.download_button(
        "Download Transaction History (CSV)",
        data=csv_text(
            ["Time (UTC)", "SKU", "Change", "Before", "After"],
            [[t.timestamp_utc, t.sku, t.change, t.before, t.after] for t in filtered],
        ),
        file_name="transaction_history.csv",
        mime="text/csv",
    )

st.divider()
st.caption("Built on inventory.py: Dictionary = products • Set = low-stock SKUs • List = transactions")
