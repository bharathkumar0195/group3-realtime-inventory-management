# Running Phase 3

Use the saturday-phase3-curveball branch and run commands from the repository root. Python 3.11 was tested. Tests and benchmarks use only the standard library.

## Get the branch and test

For an existing checkout with your changes saved:

```bash
git fetch origin
git switch saturday-phase3-curveball
git pull --ff-only
python3 -m unittest discover -s src -p 'test_*.py' -v
```

Expected: 29 tests pass. Explicit src discovery is needed; default root discovery can run zero tests.

## Quick demonstration

```bash
python3 src/benchmark_phase3.py compare --sizes 1000 --repeats 1 --output quick_check.csv
```

The example first prints A, B, C, then B, C, D after restocking A. It then verifies 500 queries and prints a timing comparison. This quick check is not the required scale evidence.

## Required scale comparison

```bash
python3 src/benchmark_phase3.py compare --sizes 10000 100000 --k 10 --seed 532 --repeats 3 --profile --output results/current/phase3_benchmark.csv
```

Allow a few minutes. Each repetition interleaves 500 updates and 500 queries. Verification happens before timing. Full inventory snapshots around every query can make verification slow at 100,000 products; that work is excluded from measured totals.

The CSV stores all timing samples, workload parameters, environment, and inventory-code checksum. Four text files alongside it contain separate cProfile reports. The printed table shows median total seconds and baseline time divided by optimized time. Profile durations include instrumentation overhead and should not replace timeit totals.

The command refreshes the current evidence files. Earlier measurements stay under results/earlier. Compare both algorithms within the same run. For controlled future process runs, prefix the command with PYTHONHASHSEED=532; the recorded runs did not fix hash randomization.

## Independent modes

Baseline only, without requiring the optimized method:

```bash
python3 src/benchmark_phase3.py baseline --sizes 10000 100000 --repeats 3 --output baseline_results.csv
```

Correctness and read-only checks, without timings:

```bash
python3 src/benchmark_phase3.py verify --sizes 10000 100000 --k 10
```

Do not use Python -O because it disables assertions. The earlier benchmark_urgent.py command delegates to this same runner; there is no second benchmark implementation.

## Export the product input

The benchmark generates data in memory. To inspect it as a CSV:

```bash
PYTHONPATH=src python3 - <<'PYTHON'
import csv
from phase3_data import generate_workload

products, _ = generate_workload(10000, 532)
with open("inventory_input.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["sku", "name", "quantity", "min_stock"])
    writer.writerows(products)
PYTHON
```

This exports products only. The benchmark still generates products and its 500 updates internally; it does not read this CSV.

## Reuse the query

In a script under src:

```python
from inventory import InventoryManager

store = InventoryManager()
store.add_product("A", "Item A", 2, 10)
store.add_product("B", "Item B", 0, 8)
for product in store.top_k_urgent(10):
    print(product.sku, product.min_stock - product.quantity)
```

Results rank shortfall descending, then SKU ascending. Only products at or below minimum stock qualify. Zero k returns an empty list; negative, Boolean, or non-integer k raises ValueError. Use add_product and adjust_stock for updates.

See [changes and speedups](PHASE3_CHANGES.md) for the measured results and interpretation.
