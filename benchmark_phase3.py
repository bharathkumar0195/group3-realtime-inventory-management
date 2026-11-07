"""Group 3 Person 3 experiment: baseline, verify, and compare modes.

Examples (from src):
  python benchmark_phase3.py baseline --sizes 10000
  python benchmark_phase3.py verify --sizes 10000 100000
  python benchmark_phase3.py compare --sizes 10000 100000 --repeats 3
"""
import argparse
import csv
import hashlib
import platform
import statistics
import timeit
from pathlib import Path

from phase3_data import build_store, generate_workload


def full_sort(store, k):
    """Timed baseline: use the SAME low-stock set as the optimized method."""
    records = (store.products[sku] for sku in store.low_stock)
    return sorted(records, key=lambda p: (p.quantity - p.min_stock, p.sku))[:k]


def catalog_oracle(store, k):
    """Independent correctness oracle: scan ALL products, not the index."""
    eligible = (p for p in store.products.values()
                if p.quantity <= p.min_stock)
    return sorted(eligible, key=lambda p: (p.quantity - p.min_stock, p.sku))[:k]


def values(products):
    return tuple((p.sku, p.quantity, p.min_stock) for p in products)


def state(store):
    return (
        {sku: (p.name, p.quantity, p.min_stock)
         for sku, p in store.products.items()},
        set(store.low_stock),
        tuple(store.transactions),
    )


def verify(rows, updates, k=10):
    """Compare full ordered answers after every update and check read-only behavior."""
    store = build_store(rows)
    optimized = getattr(store, "top_k_urgent", None)
    if optimized is None:
        raise RuntimeError("Verification requires Person 1's top_k_urgent implementation")
    for sku, delta in updates:
        store.adjust_stock(sku, delta)
        before = state(store)
        expected = values(catalog_oracle(store, k))
        actual = values(optimized(k))
        if actual != expected:
            raise AssertionError(f"Mismatch after update {sku} {delta:+d}: {actual} != {expected}")
        if state(store) != before:
            raise AssertionError("Urgency query changed inventory or transaction history")
    return len(updates)


def run_workload(store, updates, query, k=10):
    """Time only interleaved updates and queries; exclude building the store."""
    results = []
    for sku, delta in updates:
        store.adjust_stock(sku, delta)
        results.append(values(query(store, k)))
    return results


def measure(rows, updates, query, k=10):
    store = build_store(rows)  # excluded from timing
    results = []
    elapsed = timeit.Timer(
        lambda: results.append(run_workload(store, updates, query, k))
    ).timeit(number=1)
    if len(store.transactions) != len(updates):
        raise AssertionError("Unexpected number of transactions")
    return elapsed, results[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("baseline", "verify", "compare"))
    parser.add_argument("--sizes", type=int, nargs="+", default=[10000, 100000])
    parser.add_argument("--seed", type=int, default=532)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--k", type=int, default=10)
    parser.add_argument("--output", type=Path, default=Path("phase3_benchmark_results.csv"))
    args = parser.parse_args()
    if args.repeats < 1 or args.k < 0 or any(n < 250 for n in args.sizes):
        parser.error("repeats >= 1, k >= 0, and all sizes >= 250 are required")
    if not __debug__:
        parser.error("Do not use python -O for benchmark verification")

    sha = hashlib.sha256(Path(__file__).with_name("inventory.py").read_bytes()).hexdigest()
    samples = []
    summary = []
    for n in args.sizes:
        rows, updates = generate_workload(n, args.seed)
        if args.mode == "verify":
            count = verify(rows, updates, args.k)
            print(f"PASS: {n:,} products; {count} queries matched catalog oracle; query read-only")
            continue
        if args.mode == "compare":
            verify(rows, updates, args.k)  # oracle stays outside timing
        for rep in range(args.repeats):
            methods = [("sort", full_sort)]
            if args.mode == "compare":
                # Alternate execution order across repetitions.
                methods.append(("heap", lambda store, k: store.top_k_urgent(k)))
                if rep % 2:
                    methods.reverse()
            outputs = {}
            for name, query in methods:
                elapsed, result = measure(rows, updates, query, args.k)
                outputs[name] = result
                samples.append({
                    "mode": args.mode, "n": n, "seed": args.seed, "k": args.k,
                    "queries": len(updates), "updates": len(updates),
                    "repetition": rep + 1, "method": name,
                    "total_seconds": elapsed,
                    "python": platform.python_version(),
                    "platform": platform.platform(), "inventory_sha256": sha,
                })
                print(f"{n:,} products, run {rep+1}, {name}: {elapsed:.6f} s", flush=True)
            if args.mode == "compare" and outputs["sort"] != outputs["heap"]:
                raise AssertionError("Timed baseline and optimized answers differ")
        medians = {
            method: statistics.median(s["total_seconds"] for s in samples
                                      if s["n"] == n and s["method"] == method)
            for method in (("sort", "heap") if args.mode == "compare" else ("sort",))
        }
        if args.mode == "compare":
            summary.append((n, medians["sort"], medians["heap"],
                            medians["sort"] / medians["heap"]))
        else:
            summary.append((n, medians["sort"]))

    if samples:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(samples[0]))
            writer.writeheader()
            writer.writerows(samples)
        print(f"Measurements saved to {args.output}")
    if args.mode == "compare":
        print("Products | Full sort (s) | Heap (s) | Speedup")
        for n, sort, heap, ratio in summary:
            print(f"{n:>8,} | {sort:>13.3f} | {heap:>8.3f} | {ratio:.2f}x")
    elif args.mode == "baseline":
        print("Products | Full sort median (s)")
        for n, seconds in summary:
            print(f"{n:>8,} | {seconds:.3f}")


if __name__ == "__main__":
    main()
