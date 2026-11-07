# Running the Phase 3 urgency query

Use the saturday-phase3-curveball branch. Run the commands below from the repository root. The core tests and benchmark use only the Python standard library, tested with Python 3.11. Streamlit is not needed.

## Get the code

For a new checkout:

```bash
git clone --branch saturday-phase3-curveball https://github.com/bharathkumar0195/group3-realtime-inventory-management.git
cd group3-realtime-inventory-management
```

For an existing checkout with your own changes saved:

```bash
git fetch origin
git switch saturday-phase3-curveball
git pull --ff-only
```

## Run the tests

```bash
python3 -m unittest discover -s src -p 'test_*.py' -v
```

Expected: 22 tests pass. Use the explicit src directory; default discovery from the repository root can run zero tests.

## Run the demonstration and benchmarks

For a quick check on 1,000 products:

```bash
python3 src/benchmark_urgent.py --sizes 1000 --repeats 1 --output quick_check.csv
```

The opening example prints A, B, C. After restocking A, it prints B, C, D. The script then checks query results and prints a timing table. The quick check is not the required scale evidence.

For the required 10,000- and 100,000-product measurements, with separate profiler reports:

```bash
python3 src/benchmark_urgent.py --profile --output results/urgent_benchmark.csv
```

Allow a few minutes. Each method runs three times at each scale. Every timed run performs 500 queries with k=10 interleaved with 500 valid stock updates. The final table shows median total seconds and speedup. The CSV preserves every timing sample and the environment. Four text files alongside it contain separate cProfile reports for both methods and scales.

To measure without collecting profiles, omit --profile. Do not run Python with -O, which disables correctness assertions. Timings vary between machines; compare both methods within the same run.

## Use the method in another script

Put your script under src so it can import inventory:

```python
from inventory import InventoryManager

store = InventoryManager()
store.add_product("A", "Item A", 2, 10)
store.add_product("B", "Item B", 0, 8)

for product in store.top_k_urgent(10):
    shortfall = product.min_stock - product.quantity
    print(product.sku, product.quantity, shortfall)
```

The query includes products at or below minimum stock, ranks shortfall largest first, and breaks ties by SKU ascending. It returns at most k existing Product records without changing stock or history. Zero returns an empty list; invalid k raises ValueError. Keep updates through add_product and adjust_stock because the inherited Product records remain mutable.

## What the comparison measures

The baseline fully sorts the same low-stock records that the optimized method examines. The optimized method uses heap selection to retain only the best k candidates. For small k greater than one, this changes selection from O(m log m) to O(m log k), where m is the number of low-stock products. Both still scan eligible records.

Seed 532 generates quantities from 0 through 40 with minimum stock 20. The first 250 products start at 20 and each receive +1 followed by -2, crossing the low-stock boundary in both directions. The generator is in generate_workload inside src/benchmark_urgent.py and is committed with the benchmark.

Setup, validation, and profiling are outside the timeit measurements. Each repetition rebuilds identical starting stores and alternates which method runs first. An untimed full-catalog reference checks all 500 query results at each scale. Timed output lists and final inventory state are also checked.

The checked-in CSV and profiles record one local synthetic experiment. They are not a guarantee for every distribution or machine. Any separate instructor-supplied harness still needs its own run. This branch contains the query and reproducible evidence; the complete optimization notes, live defense, final appendix, and phase freeze are separate remaining deliverables.

## Recorded results

The checked-in run used Python 3.11.16 on macOS ARM64. These are median totals from three repetitions, each containing 500 queries and 500 updates:

| Products | Full sort | Heap selection | Speedup |
|---|---:|---:|---:|
| 10,000 | 1.007 s | 0.355 s | 2.83x |
| 100,000 | 15.601 s | 5.901 s | 2.64x |

See [all timing samples](results/urgent_benchmark.csv), [the 100,000-product baseline profile](results/urgent_benchmark-100000-sort-profile.txt), and [the corresponding heap profile](results/urgent_benchmark-100000-heap-profile.txt). Profile durations include instrumentation overhead and are separate from the timeit totals above.
