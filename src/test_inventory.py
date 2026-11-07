"""Tests of business invariants and primary inventory operations."""
import unittest
from inventory import InventoryManager


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.store = InventoryManager()
        self.store.add_product("LAP-01", "Laptop", 10, 3)

    def test_add_and_lookup(self):
        self.assertEqual(self.store.get_product("LAP-01").quantity, 10)
        self.assertIsNone(self.store.get_product("MISSING"))

    def test_duplicate_rejected(self):
        with self.assertRaises(ValueError):
            self.store.add_product("LAP-01", "Another", 1, 1)

    def test_receive_and_sale_update_stock(self):
        self.store.adjust_stock("LAP-01", 5)
        self.store.adjust_stock("LAP-01", -12)
        self.assertEqual(self.store.get_product("LAP-01").quantity, 3)
        self.assertIn("LAP-01", self.store.low_stock)
        self.assertEqual(len(self.store.transaction_history()), 2)

    def test_low_stock_added_and_removed(self):
        self.store.adjust_stock("LAP-01", -7)
        self.assertIn("LAP-01", self.store.low_stock)
        self.store.adjust_stock("LAP-01", 2)
        self.assertNotIn("LAP-01", self.store.low_stock)

    def test_oversell_rejected_with_no_mutation(self):
        with self.assertRaises(ValueError):
            self.store.adjust_stock("LAP-01", -11)
        self.assertEqual(self.store.get_product("LAP-01").quantity, 10)
        self.assertEqual(self.store.transaction_history(), [])

    def test_zero_adjustment_rejected(self):
        with self.assertRaises(ValueError):
            self.store.adjust_stock("LAP-01", 0)

    def test_product_creation_not_history(self):
        self.assertEqual(self.store.transaction_history(), [])

    def test_invalid_quantity_rejected(self):
        for invalid in (-1, 1.2, True, "4"):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                self.store.add_product("NEW", "New", invalid, 2)

    def test_boundary_threshold_is_low_stock(self):
        self.store.adjust_stock("LAP-01", -7)
        self.assertEqual(self.store.low_stock_report()[0].sku, "LAP-01")

    def test_report_sorted(self):
        self.store.add_product("AAA-01", "Cable", 0, 1)
        self.assertEqual([p.sku for p in self.store.inventory_report()], ["AAA-01", "LAP-01"])


if __name__ == "__main__":
    unittest.main()
