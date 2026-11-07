"""Checks for generated workloads and benchmark verification."""
import unittest
from unittest.mock import patch

from benchmark_phase3 import full_sort, measure, verify, verify_final_state
from inventory import InventoryManager
from phase3_data import build_store, generate_workload


class BenchmarkTests(unittest.TestCase):
    def test_seeded_workload_is_repeatable_and_valid(self):
        rows, updates = generate_workload(300, 532)
        self.assertEqual((rows, updates), generate_workload(300, 532))
        self.assertNotEqual(rows, generate_workload(300, 533)[0])
        self.assertEqual(len(rows), 300)
        self.assertEqual(len({row[0] for row in rows}), 300)
        self.assertEqual(len(updates), 500)
        store = build_store(rows)
        for sku, delta in updates:
            store.adjust_stock(sku, delta)
        verify_final_state(store, rows, updates)

    def test_invalid_sizes_rejected(self):
        for n in (True, None, 249, 300.5):
            with self.subTest(n=n), self.assertRaises(ValueError):
                generate_workload(n)

    def test_baseline_does_not_require_optimized_query(self):
        rows, updates = generate_workload(250)
        with patch.object(InventoryManager, "top_k_urgent", None):
            elapsed, results = measure(rows, updates, full_sort)
            self.assertGreaterEqual(elapsed, 0)
            self.assertEqual(len(results), 500)
            with self.assertRaises(RuntimeError):
                verify(rows, updates)

    def test_verification_matches_catalog_after_updates(self):
        rows, updates = generate_workload(250)
        self.assertEqual(verify(rows, updates), 500)

    def test_verification_rejects_mutating_query(self):
        rows, updates = generate_workload(250)
        original = InventoryManager.top_k_urgent

        def mutating(store, k):
            result = original(store, k)
            store.products[rows[0][0]].name = "Changed"
            return result

        with patch.object(InventoryManager, "top_k_urgent", mutating):
            with self.assertRaisesRegex(AssertionError, "changed initial inventory"):
                verify(rows, updates)

    def test_final_state_rejects_wrong_stock(self):
        rows, updates = generate_workload(250)
        store = build_store(rows)
        for sku, delta in updates:
            store.adjust_stock(sku, delta)
        store.products[rows[0][0]].quantity += 1
        with self.assertRaisesRegex(AssertionError, "final stock"):
            verify_final_state(store, rows, updates)

    def test_final_state_rejects_wrong_index(self):
        rows, updates = generate_workload(250)
        store = build_store(rows)
        for sku, delta in updates:
            store.adjust_stock(sku, delta)
        store.low_stock.clear()
        with self.assertRaisesRegex(AssertionError, "low-stock membership"):
            verify_final_state(store, rows, updates)


if __name__ == "__main__":
    unittest.main()
