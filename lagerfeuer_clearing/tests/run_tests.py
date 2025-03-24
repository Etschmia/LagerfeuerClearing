#!/usr/bin/env python3
"""
Script to run all tests for the Lagerfeuer Clearing application.
"""

import unittest


def main():
    """Run all tests for the application."""
    print("Running ExpenseManager tests...")
    unittest.main(module="lagerfeuer_clearing.tests.test_expense_manager")


if __name__ == "__main__":
    main()
