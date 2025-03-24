#!/usr/bin/env python3
"""
Example usage of the ExpenseManager class for a weekend trip scenario.
"""

from lagerfeuer_clearing.core import ExpenseManager


def main():
    """Run the weekend trip example."""
    # Create a new expense manager with empty data
    manager = ExpenseManager()

    # Define the people involved in the trip
    people = ["Alice", "Bob", "Charlie", "Diana", "Eve"]
    for person in people:
        manager.persons.append(person)

    # Define groups
    manager.groups = {
        "Everyone": people[:],
        "Drivers": ["Alice", "Charlie"],
        "Hikers": ["Alice", "Bob", "Diana"],
        "Cooking": ["Bob", "Charlie", "Eve"],
    }

    # Add expenses
    manager.add_or_update_expense("Alice", 250, "Everyone", "Cabin rental")
    manager.add_or_update_expense("Bob", 120, "Everyone", "Groceries")
    manager.add_or_update_expense("Charlie", 80, "Drivers", "Gas")
    manager.add_or_update_expense("Diana", 35, "Hikers", "Trail fees")
    manager.add_or_update_expense("Eve", 65, "Cooking", "Special ingredients")
    manager.add_or_update_expense("Bob", 40, "Everyone", "Drinks")

    # Add prepayments
    manager.add_or_update_prepayment("Charlie", 50, "Alice")
    manager.add_or_update_prepayment("Diana", 30, "Bob")

    # Calculate and display the summary
    print("WEEKEND TRIP EXPENSE SUMMARY")
    print("============================")
    print(manager.get_summary())

    # Example of updating an expense
    print("\n\nAFTER UPDATING GAS EXPENSE TO $100")
    print("==================================")
    # Find the index of the gas expense
    gas_index = next((i for i, e in enumerate(manager.expenses) if e["subject"] == "Gas"), None)
    if gas_index is not None:
        manager.add_or_update_expense("Charlie", 100, "Drivers", "Gas", gas_index)
        print(manager.get_summary())

    # Example of removing a person from a group
    print("\n\nAFTER REMOVING EVE FROM COOKING GROUP")
    print("=====================================")
    manager.remove_person_from_group("Eve", "Cooking")
    # Update the expense to be split among remaining cooking group members
    cooking_index = next(
        (i for i, e in enumerate(manager.expenses) if e["subject"] == "Special ingredients"), None
    )
    if cooking_index is not None:
        # We need to change the expense to be paid by someone else in the cooking group
        manager.add_or_update_expense("Bob", 65, "Cooking", "Special ingredients", cooking_index)
        print(manager.get_summary())


if __name__ == "__main__":
    main()
