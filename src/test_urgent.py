"""Checks for urgency ranking and unchanged inventory state."""
import random
import unittest
from dataclasses import asdict

from inventory import InventoryManager


def state(store):
    return (
        {sku: asdict(product) for sku, product in store.products.items()},
        set(store.low_stock),
        list(store.transactions),
    )


def reference_skus(store, k):
    # Scan the catalog independently of the maintained low-stock set.
    eligible = [p for p in store.products.values() if p.quantity <= p.min_stock]
    ordered = sorted(eligible, key=lambda p: (p.quantity - p.min_stock, p.sku))
    return [p.sku for p in ordered[:k]]


class UrgentQueryTests(unittest.TestCase):
    def setUp(self):
        self.store = InventoryManager()
        for sku, quantity, minimum in [
            ("E", 11, 10), ("B", 0, 8), ("D", 10, 10),
            ("C", 5, 10), ("A", 2, 10),
        ]:
            self.store.add_product(sku, sku, quantity, minimum)

    def skus(self, k):
        return [p.sku for p in self.store.top_k_urgent(k)]

    def test_rank_and_sku_tie(self):
        self.assertEqual(self.skus(3), ["A", "B", "C"])

    def test_single_result(self):
        self.assertEqual(self.skus(1), ["A"])

    def test_zero_returns_empty(self):
        self.assertEqual(self.skus(0), [])

    def test_exact_and_excessive_k(self):
        for k in (4, 10, 10**30):
            with self.subTest(k=k):
                self.assertEqual(self.skus(k), ["A", "B", "C", "D"])

    def test_invalid_k_preserves_state(self):
        before = state(self.store)
        for k in (-1, True, False, 1.5, "3", None):
            with self.subTest(k=k), self.assertRaises(ValueError):
                self.store.top_k_urgent(k)
            self.assertEqual(state(self.store), before)

    def test_empty_inventory(self):
        self.assertEqual(InventoryManager().top_k_urgent(10), [])

    def test_no_eligible_products(self):
        store = InventoryManager()
        store.add_product("X", "X", 5, 4)
        self.assertEqual(store.top_k_urgent(10), [])

    def test_zero_quantity_and_threshold_equality(self):
        store = InventoryManager()
        store.add_product("Z", "Z", 0, 0)
        store.add_product("A", "A", 0, 3)
        self.assertEqual([p.sku for p in store.top_k_urgent(10)], ["A", "Z"])

    def test_updates_change_rank_and_eligibility(self):
        self.store.adjust_stock("A", 9)
        self.assertEqual(self.skus(3), ["B", "C", "D"])
        self.store.adjust_stock("E", -10)
        self.assertEqual(self.skus(3), ["E", "B", "C"])
        self.store.add_product("F", "F", 0, 20)
        self.assertEqual(self.skus(1), ["F"])

    def test_repeated_queries_are_read_only(self):
        self.store.adjust_stock("C", -1)
        before = state(self.store)
        identities = (id(self.store.products), id(self.store.low_stock), id(self.store.transactions))
        for _ in range(3):
            for k in (0, 1, 3, 10):
                result = self.store.top_k_urgent(k)
                self.assertEqual([p.sku for p in result], reference_skus(self.store, k))
                self.assertEqual(state(self.store), before)
                self.assertTrue(all(p is self.store.products[p.sku] for p in result))
        self.assertEqual(
            (id(self.store.products), id(self.store.low_stock), id(self.store.transactions)),
            identities,
        )

    def test_ties_do_not_depend_on_insertion_order(self):
        for order in [("c", "a", "B", "A"), ("A", "B", "a", "c")]:
            store = InventoryManager()
            for sku in order:
                store.add_product(sku, sku, 1, 5)
            self.assertEqual([p.sku for p in store.top_k_urgent(3)], ["A", "B", "a"])

    def test_seeded_interleaved_updates_against_catalog_oracle(self):
        rng = random.Random(532)
        store = InventoryManager()
        for i in range(100):
            store.add_product(f"P{i:03d}", "Product", rng.randrange(41), 20)
        for _ in range(500):
            sku = f"P{rng.randrange(100):03d}"
            quantity = store.get_product(sku).quantity
            delta = rng.choice((-5, -1, 1, 5))
            if quantity + delta < 0:
                delta = 1
            store.adjust_stock(sku, delta)
            before = state(store)
            for k in (0, 1, 10, 25, 150):
                self.assertEqual(
                    [p.sku for p in store.top_k_urgent(k)], reference_skus(store, k),
                )
                self.assertEqual(state(store), before)


if __name__ == "__main__":
    unittest.main()
