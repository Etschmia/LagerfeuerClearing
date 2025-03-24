"""
Tests for the ExpenseManager class.
"""
import unittest
import os
import json
from lagerfeuer_clearing.core import ExpenseManager


class TestExpenseManager(unittest.TestCase):
    """Test cases for ExpenseManager class."""

    def setUp(self):
        """Set up a test instance with a simple dataset before each test."""
        self.manager = ExpenseManager(
            persons=["Alice", "Bob", "Charlie"],
            groups={
                "All": ["Alice", "Bob", "Charlie"],
                "AB": ["Alice", "Bob"]
            },
            expenses=[
                {"person": "Alice", "amount": 150, "group": "All", "subject": "Food"},
                {"person": "Bob", "amount": 60, "group": "AB", "subject": "Drinks"}
            ],
            prepayments=[
                {"person": "Charlie", "amount": 20, "recipient": "Alice"}
            ]
        )
        
        # For file operations tests
        self.test_file = "test_expenses.json"
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """Clean up after each test."""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_initialization(self):
        """Test that ExpenseManager initializes correctly with provided data."""
        self.assertEqual(len(self.manager.persons), 3)
        self.assertEqual(len(self.manager.groups), 2)
        self.assertEqual(len(self.manager.expenses), 2)
        self.assertEqual(len(self.manager.prepayments), 1)
        
        # Test empty initialization
        empty_manager = ExpenseManager()
        self.assertEqual(len(empty_manager.persons), 0)
        self.assertEqual(len(empty_manager.groups), 0)
        self.assertEqual(len(empty_manager.expenses), 0)
        self.assertEqual(len(empty_manager.prepayments), 0)

    def test_create_with_defaults(self):
        """Test that default data is created correctly."""
        default_manager = ExpenseManager.create_with_defaults()
        self.assertTrue(len(default_manager.persons) > 0)
        self.assertTrue(len(default_manager.groups) > 0)
        self.assertTrue(len(default_manager.expenses) > 0)
        self.assertTrue(len(default_manager.prepayments) > 0)
        
        # Verify specific default data
        self.assertIn("Tobias", default_manager.persons)
        self.assertIn("Alle", default_manager.groups)
        self.assertEqual(
            next((e for e in default_manager.expenses if e["subject"] == "Unterkunft"), {}).get("amount"),
            1300
        )

    def test_add_person(self):
        """Test adding a person to the manager."""
        self.manager.add_person("Dave")
        self.assertIn("Dave", self.manager.persons)
        self.assertEqual(len(self.manager.persons), 4)
        
        # Test adding to a group
        self.manager.add_person("Eve", "All")
        self.assertIn("Eve", self.manager.persons)
        self.assertIn("Eve", self.manager.groups["All"])
        
        # Test adding existing person (shouldn't duplicate)
        self.manager.add_person("Alice")
        self.assertEqual(len(self.manager.persons), 5)  # Shouldn't increase

    def test_remove_person_from_group(self):
        """Test removing a person from a group."""
        self.manager.remove_person_from_group("Alice", "AB")
        self.assertNotIn("Alice", self.manager.groups["AB"])
        self.assertIn("Alice", self.manager.persons)  # Still in another group
        self.assertIn("Alice", self.manager.groups["All"])
        
        # Test removing from last group (should also remove from persons)
        self.manager.remove_person_from_group("Alice", "All")
        self.assertNotIn("Alice", self.manager.persons)

    def test_add_or_update_expense(self):
        """Test adding and updating expenses."""
        # Add new expense
        self.manager.add_or_update_expense("Charlie", 75, "All", "Transport")
        self.assertEqual(len(self.manager.expenses), 3)
        
        # Update existing expense
        self.manager.add_or_update_expense("Alice", 200, "All", "Updated Food", 0)
        self.assertEqual(self.manager.expenses[0]["amount"], 200)
        self.assertEqual(self.manager.expenses[0]["subject"], "Updated Food")
        
        # Test with invalid index (should add new expense)
        self.manager.add_or_update_expense("Bob", 50, "All", "Test", 10)
        self.assertEqual(len(self.manager.expenses), 4)

    def test_remove_expense(self):
        """Test removing an expense."""
        self.manager.remove_expense(0)
        self.assertEqual(len(self.manager.expenses), 1)
        self.assertEqual(self.manager.expenses[0]["subject"], "Drinks")
        
        # Test with invalid index (should not raise error)
        self.manager.remove_expense(10)
        self.assertEqual(len(self.manager.expenses), 1)

    def test_add_or_update_prepayment(self):
        """Test adding and updating prepayments."""
        # Add new prepayment
        self.manager.add_or_update_prepayment("Bob", 30, "Charlie")
        self.assertEqual(len(self.manager.prepayments), 2)
        
        # Update existing prepayment
        self.manager.add_or_update_prepayment("Charlie", 25, "Alice", 0)
        self.assertEqual(self.manager.prepayments[0]["amount"], 25)
        
        # Test with invalid index (should add new prepayment)
        self.manager.add_or_update_prepayment("Alice", 15, "Bob", 10)
        self.assertEqual(len(self.manager.prepayments), 3)

    def test_remove_prepayment(self):
        """Test removing a prepayment."""
        self.manager.remove_prepayment(0)
        self.assertEqual(len(self.manager.prepayments), 0)
        
        # Test with invalid index (should not raise error)
        self.manager.remove_prepayment(10)
        self.assertEqual(len(self.manager.prepayments), 0)

    def test_rename_group(self):
        """Test renaming a group."""
        self.manager.rename_group("AB", "AliceBob")
        self.assertNotIn("AB", self.manager.groups)
        self.assertIn("AliceBob", self.manager.groups)
        
        # Check that expenses were updated
        drink_expense = next(e for e in self.manager.expenses if e["subject"] == "Drinks")
        self.assertEqual(drink_expense["group"], "AliceBob")
        
        # Test with non-existent group (should not change anything)
        original_groups = self.manager.groups.copy()
        self.manager.rename_group("NonExistent", "NewName")
        self.assertEqual(self.manager.groups, original_groups)
        
        # Test with duplicate target name (should not change anything)
        original_groups = self.manager.groups.copy()
        self.manager.rename_group("AliceBob", "All")
        self.assertEqual(self.manager.groups, original_groups)

    def test_calculate_balances(self):
        """Test balance calculation."""
        balances = self.manager.calculate_balances()
        
        # Test that all dictionaries are created
        self.assertIn("paid", balances)
        self.assertIn("received", balances)
        self.assertIn("owes", balances)
        self.assertIn("balance", balances)
        
        # Test specific values for the test data
        self.assertEqual(balances["paid"]["Alice"], 150)
        self.assertEqual(balances["paid"]["Bob"], 60)
        self.assertEqual(balances["paid"]["Charlie"], 20)
        
        self.assertEqual(balances["received"]["Alice"], 20)
        
        # Each person owes 150/3 = 50 for All group
        # Alice and Bob each owe 60/2 = 30 for AB group
        self.assertEqual(balances["owes"]["Alice"], 50 + 30)
        self.assertEqual(balances["owes"]["Bob"], 50 + 30)
        self.assertEqual(balances["owes"]["Charlie"], 50)
        
        # Balance = paid - received - owes
        self.assertAlmostEqual(balances["balance"]["Alice"], 150 - 20 - 80, places=2)
        self.assertAlmostEqual(balances["balance"]["Bob"], 60 - 0 - 80, places=2)
        self.assertAlmostEqual(balances["balance"]["Charlie"], 20 - 0 - 50, places=2)

    def test_calculate_transactions(self):
        """Test transaction calculation."""
        results = self.manager.calculate_transactions()
        transactions = results["transactions"]
        
        # Check that we have transactions
        self.assertTrue(len(transactions) > 0)
        
        # Validate transaction structure
        transaction = transactions[0]
        self.assertIn("from", transaction)
        self.assertIn("to", transaction)
        self.assertIn("amount", transaction)
        
        # Sum of all transactions should be our total debt
        total_transaction_amount = sum(t["amount"] for t in transactions)
        total_debt = sum(abs(b) for b in results["balances"]["balance"].values() if b < 0)
        self.assertAlmostEqual(total_transaction_amount, total_debt, places=2)

    def test_get_summary(self):
        """Test summary generation."""
        summary = self.manager.get_summary()
        
        # Check that the summary is a non-empty string
        self.assertTrue(isinstance(summary, str))
        self.assertTrue(len(summary) > 0)
        
        # Check that the summary contains expected sections
        self.assertIn("Ausgangspunkt der Reisekostenaufteilung", summary)
        self.assertIn("Ausgaben", summary)
        self.assertIn("Anzahlungen", summary)
        self.assertIn("Transaktionen die jetzt folgen müssen", summary)
        self.assertIn("Überprüfung der Kosten", summary)

    def test_save_and_load_file(self):
        """Test saving and loading from file."""
        # Save the manager state
        self.manager.save_to_file(self.test_file)
        self.assertTrue(os.path.exists(self.test_file))
        
        # Load the state into a new manager
        loaded_manager = ExpenseManager.load_from_file(self.test_file)
        
        # Verify the loaded data matches the original
        self.assertEqual(len(loaded_manager.persons), len(self.manager.persons))
        self.assertEqual(len(loaded_manager.groups), len(self.manager.groups))
        self.assertEqual(len(loaded_manager.expenses), len(self.manager.expenses))
        self.assertEqual(len(loaded_manager.prepayments), len(self.manager.prepayments))
        
        # Check specific data points
        self.assertIn("Alice", loaded_manager.persons)
        self.assertIn("All", loaded_manager.groups)
        
        # Check that file loading handles missing files
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        default_loaded = ExpenseManager.load_from_file(self.test_file)
        self.assertTrue(len(default_loaded.persons) > 0)  # Should load defaults


if __name__ == "__main__":
    unittest.main() 