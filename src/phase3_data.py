"""Deterministic inventory datasets for Group 3 Phase 3 benchmarks.

No dependency on the optimized urgency query. The same rows and updates are
used for baseline, verification, and comparison.
"""
import random
from inventory import InventoryManager


def generate_workload(n: int, seed: int = 532):
    """Return (product rows, 500 updates) with ties and threshold crossings."""
    if isinstance(n, bool) or not isinstance(n, int) or n < 250:
        raise ValueError("n must be an integer >= 250")
    rng = random.Random(seed)
    rows = [
        (f"SKU{i:06d}", f"Product {i}",
         20 if i < 250 else rng.randrange(41), 20)
        for i in range(n)
    ]
    # 250 SKUs each cross the threshold twice: 20 -> 21 -> 19.
    updates = [(f"SKU{i:06d}", delta)
               for i in range(250) for delta in (1, -2)]
    return rows, updates


def build_store(rows):
    """Build a fresh store; callers should do this outside timed sections."""
    store = InventoryManager()
    for row in rows:
        store.add_product(*row)
    return store
