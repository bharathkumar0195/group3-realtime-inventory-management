# Real Time Inventory Management

MSCS 532 residency project. The program registers products, finds them by SKU, adjusts stock, reports low-stock products, and records successful stock changes. Phase 3 adds a read-only urgency query and reproducible performance comparisons.

- [Run guide](PHASE3_RUN.md): setup, tests, demonstrations, and benchmark modes.
- [Changes and measured speedups](PHASE3_CHANGES.md): what changed, why, results, and limitations.
- [Current results](results/current/): integrated benchmark samples and profiles.
- [Earlier results](results/earlier/): preserved measurements from the original benchmark runner.

## Run

Run from the repository root. Core code uses the Python standard library, tested with Python 3.11.

```bash
python3 -m unittest discover -s src -p 'test_*.py' -v
python3 src/main.py
```

For a quick benchmark:

```bash
python3 src/benchmark_phase3.py compare --sizes 1000 --repeats 1 --output quick_check.csv
```

For the optional Streamlit interface:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m streamlit run src/app.py
```

Open the local URL printed by Streamlit. The interface starts with four sample products. Core tests and benchmarks do not require Streamlit.

## Code

| File | Responsibility |
|---|---|
| src/inventory.py | Product dictionary, low-stock set, transaction list, and urgency query |
| src/main.py | Command-line inventory menu |
| src/app.py | Optional web interface |
| src/phase3_data.py | Seeded products and stock updates |
| src/benchmark_phase3.py | Baseline, verification, comparison, and profiling |
| src/benchmark_urgent.py | Compatibility entry point for earlier commands |
| src/test_inventory.py | Inherited inventory tests |
| src/test_urgent.py | Urgency-query tests |
| src/test_phase3_benchmark.py | Generator and benchmark-validation tests |

The inherited design brief, implementation notes, handoff, and prior-phase appendix remain available at the root. They describe earlier phases; use the Phase 3 documents above for current commands and results.

## Limits

Inventory is single-process and held in memory. It is lost when the process or web session resets. CSV downloads are exports, not persistent storage. Use manager methods to change stock; directly editing a Product can leave its low-stock membership stale.
