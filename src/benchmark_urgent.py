"""Compare full sorting with top_k_urgent on a repeatable update/query workload."""
import argparse
import cProfile
import csv
import hashlib
import platform
import pstats
import random
import statistics
import timeit
from pathlib import Path

from inventory import InventoryManager


def generate_workload(n, seed):
    if n < 250:
        raise ValueError("Use at least 250 products for the 500-update workload")
    rng = random.Random(seed)
    rows = [
        (f"SKU{i:06d}", f"Product {i}", 20 if i < 250 else rng.randrange(41), 20)
        for i in range(n)
    ]
    updates = [(f"SKU{i:06d}", delta) for i in range(250) for delta in (1, -2)]
    return rows, updates


def build_store(rows):
    store = InventoryManager()
    for row in rows:
        store.add_product(*row)
    return store


def full_sort(store, k):
    records = (store.products[sku] for sku in store.low_stock)
    return sorted(records, key=lambda p: (p.quantity - p.min_stock, p.sku))[:k]


def heap_query(store, k):
    return store.top_k_urgent(k)


def values(records):
    return tuple((p.sku, p.quantity, p.min_stock) for p in records)


def snapshot(store):
    return (
        {sku: (p.name, p.quantity, p.min_stock) for sku, p in store.products.items()},
        set(store.low_stock),
        tuple(store.transactions),
    )


def verify(rows, updates):
    store = build_store(rows)
    before = snapshot(store)
    store.top_k_urgent(10)
    assert snapshot(store) == before, "Query changed inventory state"
    for sku, delta in updates:
        store.adjust_stock(sku, delta)
        eligible = [p for p in store.products.values() if p.quantity <= p.min_stock]
        expected = sorted(eligible, key=lambda p: (p.quantity - p.min_stock, p.sku))[:10]
        assert values(store.top_k_urgent(10)) == values(expected), "Incorrect query result"
    verify_final_state(store, rows, updates)


def verify_final_state(store, rows, updates):
    expected = {row[0]: row[2] for row in rows}
    for sku, delta in updates:
        expected[sku] += delta
    assert len(store.transactions) == len(updates), "Unexpected transaction count"
    assert all(p.quantity == expected[sku] for sku, p in store.products.items())
    assert store.low_stock == {
        sku for sku, p in store.products.items() if p.quantity <= p.min_stock
    }, "Incorrect low-stock membership"


def run_workload(store, updates, query):
    results = []
    for sku, delta in updates:
        store.adjust_stock(sku, delta)
        results.append(values(query(store, 10)))
    return results


def demo():
    store = InventoryManager()
    for sku, quantity, minimum in [("E", 11, 10), ("B", 0, 8), ("D", 10, 10),
                                   ("C", 5, 10), ("A", 2, 10)]:
        store.add_product(sku, sku, quantity, minimum)
    print("Demo top three:", [p.sku for p in store.top_k_urgent(3)], flush=True)
    store.adjust_stock("A", 9)
    print("After restocking A:", [p.sku for p in store.top_k_urgent(3)], flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sizes", type=int, nargs="+", default=[10000, 100000])
    parser.add_argument("--seed", type=int, default=532)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output", type=Path, default=Path("benchmark_results.csv"))
    parser.add_argument("--profile", action="store_true", help="Save separate cProfile reports")
    args = parser.parse_args()
    if args.repeats < 1 or any(n < 250 for n in args.sizes):
        parser.error("repeats must be positive and sizes must be at least 250")
    if not __debug__:
        parser.error("Run without -O: correctness assertions must be enabled")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    inventory_hash = hashlib.sha256(Path(__file__).with_name("inventory.py").read_bytes()).hexdigest()
    samples = []
    summary = []
    demo()
    for n in args.sizes:
        rows, updates = generate_workload(n, args.seed)
        verify(rows, updates)
        initial_eligible = sum(row[2] <= row[3] for row in rows)
        print(f"{n:,} products: all 500 queries match the catalog reference", flush=True)
        for repetition in range(args.repeats):
            methods = [("sort", full_sort), ("heap", heap_query)]
            if repetition % 2:
                methods.reverse()
            outputs = {}
            for name, query in methods:
                store = build_store(rows)
                holder = []

                def timed_run():
                    holder.append(run_workload(store, updates, query))

                seconds = timeit.Timer(timed_run).timeit(number=1)
                outputs[name] = holder[0]
                verify_final_state(store, rows, updates)
                samples.append({
                    "n": n, "seed": args.seed, "k": 10, "queries": 500, "updates": 500,
                    "initial_eligible": initial_eligible, "repetition": repetition + 1,
                    "method": name, "total_seconds": seconds,
                    "python": platform.python_version(), "platform": platform.platform(),
                    "inventory_sha256": inventory_hash,
                })
                print(f"  Run {repetition + 1} {name}: {seconds:.6f} s", flush=True)
            assert outputs["sort"] == outputs["heap"], "Timed runs returned different results"
        medians = {
            name: statistics.median(s["total_seconds"] for s in samples
                                    if s["n"] == n and s["method"] == name)
            for name in ("sort", "heap")
        }
        summary.append((n, medians["sort"], medians["heap"], medians["sort"] / medians["heap"]))
        with args.output.open("w", newline="") as output:
            writer = csv.DictWriter(output, fieldnames=list(samples[0]), lineterminator="\n")
            writer.writeheader()
            writer.writerows(samples)
        if args.profile:
            import io

            for name, query in [("sort", full_sort), ("heap", heap_query)]:
                store = build_store(rows)
                profiler = cProfile.Profile()
                profiler.runcall(run_workload, store, updates, query)
                report = args.output.with_name(f"{args.output.stem}-{n}-{name}-profile.txt")
                output = io.StringIO()
                pstats.Stats(profiler, stream=output).strip_dirs().sort_stats("cumulative").print_stats(20)
                report.write_text(output.getvalue().rstrip() + "\n")
    print("\nProducts | Full sort (s) | Heap (s) | Speedup")
    for n, sort, heap, speedup in summary:
        print(f"{n:>8,} | {sort:>13.3f} | {heap:>8.3f} | {speedup:.2f}x")
    print(f"Raw measurements saved to {args.output}")


if __name__ == "__main__":
    main()
