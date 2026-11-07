# Implementation Notes: Phase 2 Proof of Concept

**Project:** Group 3, Real-Time Inventory Management System (Python)
**Phase 2 team:** Naga Naveena Chennupati, Narendra Reddy Gangireddy, Fortunato Jose Hernandez Ferrer, Namratha Kondi, Pawan Sharma · **Date:** November 7, 2026 · **Tag:** `phase2-final`

## What we built

We implemented Group 3's Phase 1 design as a single-process, in-memory Python program. Everything lives in one class, `InventoryManager` (`inventory.py`), which uses the three structures the brief selected:

- `products`: a `dict` mapping SKU to `Product`, the single source of truth
- `low_stock`: a `set` of SKUs whose `quantity <= min_stock`
- `transactions`: a `list` of `Transaction` records, one for each successful stock change

`main.py` is an interactive menu covering all five functional requirements, and `test_inventory.py` holds 10 unit tests.

| Requirement | Method | Time |
|---|---|---|
| FR1 add a unique product | `add_product(sku, name, quantity, min_stock)` | O(1) average |
| FR2 search by SKU | `get_product(sku)` returns `Product` or `None` | O(1) average |
| FR3 receive or sell | `adjust_stock(sku, change)` (positive = receive, negative = sell) | O(1) average |
| FR4 low-stock list | `low_stock_report()`, sorted by SKU | O(k log k) |
| FR5 inventory report | `inventory_report()`, sorted by SKU | O(n log n) |
| Log of adjustments | `transaction_history(sku=None)` | O(t) |

Here n is the number of products, k the number of low-stock products, and t the number of logged transactions.

**The invariant.** After every successful call, no quantity is negative, and `low_stock` contains exactly the SKUs where `quantity <= min_stock`. `adjust_stock` checks everything (valid SKU, non-zero integer change, product exists, no overselling) before changing anything, so a rejected call leaves the quantity, the set, and the history untouched. `_update_low_stock` is the only place the set changes, and both `add_product` and `adjust_stock` call it.

## How we read the brief

- **Confirmed by Group 3** during the consultation window: a zero adjustment is rejected, stock can never go negative, and only successful stock adjustments are logged. Adding a product is not.
- **Missing SKU:** `get_product` returns `None`, following the brief's "return not-found response," and the menu prints "Product not found." `adjust_stock` raises `KeyError`, since changing stock for a product that doesn't exist is an error rather than a normal result.
- **Low-stock boundary:** inclusive, as written. A product exactly at its threshold is low stock.
- **Input rules:** SKUs and names are trimmed and can't be empty. SKUs are case-sensitive. Quantities must be non-negative integers, and `True`/`False` are rejected, since Python treats them as 1 and 0.
- **Naming:** the brief's `reorder_level` is called `min_stock` in the code. They mean the same thing.
- **History records:** each `Transaction` stores a UTC timestamp, the SKU, the change, and the quantity before and after, so every entry shows exactly what happened.

## Our one design change: sorted reports

Both reports return products sorted by SKU. The brief says full reports "do not require sorted order" and sets them at O(n), with the low-stock list at O(k). We chose sorted output because store staff read these reports, and finding a product in a sorted list is much easier. The cost is O(n log n) for the full report and O(k log k) for the low-stock list. We think that's acceptable under Group 3's own workload estimates: full reports run about twice a second, and k is usually far smaller than n. The structures themselves are unchanged. If Phase 3 finds the sorting is a bottleneck, removing `sorted()` from the core and sorting only in the menu restores the brief's original bounds.

## What we deferred

Saving data between runs, multiple users or concurrent access, deleting products, and editing a product's name or threshold are all out of scope, as the brief states.

## Known weaknesses: where Phase 3 should look first

1. **`Product` can be edited from outside.** `get_product` returns the stored record itself, so a caller could change `.quantity` directly and leave `low_stock` out of sync. All changes inside the class go through `adjust_stock`, which is safe; making `Product` a frozen dataclass would close the gap.
2. **History filtering scans everything.** `transaction_history(sku)` is O(t) even for one SKU. A `dict` from SKU to its transactions would make it proportional to that SKU's history.
3. **History grows without limit.** Memory rises with every transaction.
4. **Sorting in the reports** is the price of our design change (see above), and the first thing to measure on a 100,000-product dataset.
5. **Built-in exceptions.** Overselling and bad input both raise `ValueError`, so callers can only tell them apart by the message.
6. **Small menu issues.** Pressing Ctrl-D at a prompt crashes the menu, because `EOFError` isn't caught. Typing letters for a number shows Python's default error text. A missing SKU prints with extra quotes, because `KeyError` wraps its message in quotes. `asdict` and `math` are imported but never used.

## How to run and test

Requires Python 3.10 or newer, with no other dependencies.

```bash
python main.py              # interactive menu (the demo)
python -m unittest -v       # 10 tests
```

**Suggested demo run:** add a product → try the same SKU again (rejected) → find it, then a missing SKU → receive stock → sell some → try to oversell (rejected) → sell until it reaches its threshold and check option 5 → receive one unit and check option 5 again → show the inventory report and the transaction history.

**What the tests cover:** add and lookup (including a missing SKU), duplicate SKUs, receive and sell, low stock appearing and disappearing, oversell rejected with no change, zero adjustment rejected, product creation not logged, invalid quantities (−1, 1.2, `True`, "4"), the threshold boundary, and the sorted report.
