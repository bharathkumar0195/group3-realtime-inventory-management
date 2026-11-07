# Group 3 — Real-Time Inventory Management System (Python)
**Phase 1: Design Sprint | November 6, 2026**

## 1. Application Context and Scope
Small retail stores need immediate, accurate stock visibility when employees receive or sell products. This project proposes a **single-process Python command-line proof of concept** that adds products, looks up stock by unique product ID (SKU), receives stock, processes sales, identifies low-stock products, and displays an inventory report. “Real-time” here means changes are visible immediately within the running application; distributed synchronization, persistence, and multiple simultaneous users are out of scope for this weekend.

**Product model:** `sku: str` (unique), `name: str`, `quantity: int >= 0`, `reorder_level: int >= 0`. Sample: `P102, Mouse, 5, 10`. A product is low-stock when `quantity <= reorder_level`.

**Functional requirements:** FR1 add unique product; FR2 search by SKU; FR3 receive/sell positive quantities without overselling; FR4 list low-stock products; FR5 display all products. Reject missing SKUs, duplicate SKUs, invalid quantities, and insufficient stock. Log successful stock adjustments.

## 2. Workload First (Design Assumptions, Not Benchmarks)
Assume **10,000 SKUs initially**, growing to **100,000**. The workload is lookup- and update-heavy; ranges and ordered reporting are occasional. Peak frequencies below are illustrative, not claimed throughput.

| Operation | Estimated peak frequency | Required behavior / tolerance |
|---|---:|---|
| Find product by SKU | 100/sec | Exact lookup, prompt response |
| Receive stock / sell item | 50/sec | Accurate, immediate stock update |
| Add new product | 5/sec | Reject duplicate SKU |
| Retrieve low-stock list | 10/sec | Current threshold status |
| Full inventory report | 2/sec | May scan all products |

## 3. Data Structure Decision Matrix
Let **n** be number of products and **k** number of low-stock products. Complexities are expected/amortized where stated; Python dictionaries and sets have pathological O(n) worst cases.

| Operation | Selected | Two plausible alternatives | Why selected / why others rejected |
|---|---|---|---|
| SKU lookup, add, update | `dict[sku] -> product` (average O(1)) | Unsorted list (O(n) lookup); balanced BST (O(log n)) | Exact-ID traffic dominates; dictionary is simple and fast. List scans scale poorly; BST preserves ordering not needed on hot path. |
| Maintain low-stock membership | `set[sku]` (average O(1) membership and update) | Full dictionary scan (O(n) per alert request); heap (top priority O(1), updates more involved) | Maintain set as stock changes, then enumerate in O(k). Scans repeat work; heap adds complexity and is best if ranking by urgency is required. |
| Append successful stock transactions | `list` (amortized O(1) append) | Linked list (O(1) append with tail, custom implementation); `deque` (O(1) append) | Standard list is adequate for append-only audit in a small POC. Linked list adds implementation cost; deque is equally viable but unnecessary without frequent left-end removals. |
| Full inventory report | Traverse dictionary values (O(n)) | Sorted array (O(n) walk); balanced BST (O(n) ordered walk) | Full reports are infrequent and do not require sorted order. If SKU sorting is requested, sort on demand in O(n log n). |

**Trade-offs:** Each product update touches the dictionary entry and updates low-stock set membership so the two remain consistent. Iterating the entire inventory is O(n), which is acceptable at the assumed report frequency. Data is lost on exit unless future phases add storage; this limitation must be stated, not concealed. No custom hash table is needed because Python `dict` meets the stated workload.

## 4. Proposed Algorithms and Interface
- `add_product(sku, name, quantity, reorder_level)`: validate, add dict record, update low-stock set.
- `get_product(sku)`: dictionary lookup; return not-found response if missing.
- `adjust_stock(sku, delta)`: verify SKU and integer change, reject resulting quantity < 0, update quantity and low-stock membership, append history event.
- `get_low_stock()`: collect product records by iterating low-stock SKU set; O(k) expected.
- `list_inventory()`: iterate product dictionary; O(n).

**Acceptance tests:** Add a new product; reject duplicate SKU; find existing/missing SKU; restock; sell successfully; reject oversell; confirm low-stock alert appears/disappears at the threshold; verify inventory report matches updated quantities. All operations must preserve `quantity >= 0` and low-stock set consistency.

**Handoff boundary:** Phase 2 team builds a working Python CLI using this interface and tests. Phase 3 measures/optimizes performance. Phase 4 audits correctness and demonstrates the program. Keep scope small enough for five-hour development sessions.
