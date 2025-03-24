#!/usr/bin/env python3
"""
Command line application for expense sharing calculations.
"""
from lagerfeuer_clearing.core import ExpenseManager


def main():
    """Run the CLI application."""
    # Create an expense manager with default data
    manager = ExpenseManager.create_with_defaults()

    # Generate and print the summary
    print(manager.get_summary())


if __name__ == "__main__":
    main() 