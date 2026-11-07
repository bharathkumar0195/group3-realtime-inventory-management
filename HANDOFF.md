# Phase 1 → Phase 2 Handoff

## What you are inheriting
A **design only**, not a working implementation. Read `DESIGN_BRIEF.md` before coding. Prioritize a working CLI and tests over extra features.

## Suggested module/API contract
Implement `InventoryManager` with:
- `add_product(sku: str, name: str, quantity: int, reorder_level: int) -> None`
- `get_product(sku: str) -> dict | None`
- `adjust_stock(sku: str, delta: int) -> None` where positive receives stock, negative sells stock
- `get_low_stock() -> list[dict]`
- `list_inventory() -> list[dict]`

Suggested internal structures: `products: dict[str, dict]`, `low_stock_skus: set[str]`, `transactions: list[dict]`. `adjust_stock` updates both inventory and alert membership; only successful adjustments enter transaction history. Use clear exceptions or error responses consistently.

## Invariants and edge cases
- Unique, nonempty SKU and product name.
- Quantity and reorder level must be nonnegative integers; reject booleans and malformed inputs as integers if practical.
- Stock must never become negative; selling unavailable units must fail without partially changing data.
- `sku in low_stock_skus` **iff** `products[sku]['quantity'] <= products[sku]['reorder_level']`.
- No duplicate product IDs; missing product is handled gracefully.

## Minimum demonstration sequence
1. Add `P101` Laptop, quantity 25, threshold 10.
2. Add `P102` Mouse, quantity 5, threshold 10 — low stock should include P102.
3. Search for P101 — quantity 25.
4. Sell 20 P101 — now quantity 5, low-stock list includes P101 and P102.
5. Restock P102 by 10 — now quantity 15, low-stock list removes P102.
6. Attempt to sell 100 P101 — reject, quantity remains 5.
7. Print full inventory and recent successful stock adjustments.

## Tests to implement
Unique SKU validation, successful lookup, not-found lookup, add/receive/sell, oversell rejection, zero-boundary threshold behavior, low-stock set consistency, transaction recording, inventory reporting.

## Deliberate non-goals
No web UI, databases, login system, multi-user concurrency, hardware integration, complex forecasting, or cloud deployment. These are potential future extensions, not Phase 2 requirements.

## Questions to confirm during Phase 2 handover
- Should a zero-delta adjustment be allowed or rejected? (Suggested: reject.)
- Should reports be sorted? (Suggested: no; optional enhancement.)
- Does the professor require specific input/output formatting? Follow the rubric if so.

## Version checkpoint
Inherited baseline tag: `phase1-final` (create only after files are finalized). Do not overwrite the tag. New teams should branch from it or use the professor-assigned repo workflow.



# Phase 2 → Phase 3 Handof

**Project:** Group 3 – Real-Time Inventory Management System

## Phase 2 – Completed

Developed a Python-based inventory management system with a Streamlit UI supporting seven functions:

1. Add Product
2. Find Product by SKU
3. Receive Stock
4. Sell Stock
5. Low-Stock Alerts
6. Inventory Report
7. Transaction History

**Data Structures:**
- Dictionary – Fast product lookup (O(1) average)
- Set – Low-stock tracking (O(1) average)
- List – Transaction history (O(1) amortized append)

**Testing:** All 10 unit tests passed.

## Phase 3 – Planned Enhancements

- Integrate SQLite for persistent data storage.
- Connect the database with Python logic and Streamlit UI.
- Improve input validation and error handling.
- Enhance inventory reporting.
- Perform integration testing.

## Phase 4 – Final Delivery

- Conduct end-to-end and performance testing.
- Fix bugs and improve application reliability.
- Prepare deployment instructions.
- Finalize documentation and README.
- Complete the final project presentation.

## Handoff Summary

Phase 2 delivered a working inventory management prototype.

Phase 3 will focus on database integration and system improvements.

Phase 4 will focus on testing, deployment preparation, and final project delivery.
