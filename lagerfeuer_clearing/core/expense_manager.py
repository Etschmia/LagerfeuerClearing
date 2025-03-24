"""
Core class for expense tracking and calculation to support shared expense management.
"""
from collections import defaultdict
import json
import os


class ExpenseManager:
    """Core class to handle expense tracking and calculations for group expenses."""
    
    def __init__(self, persons=None, groups=None, expenses=None, prepayments=None):
        """Initialize the expense manager with the provided data or empty structures.
        
        Args:
            persons: List of person names
            groups: Dictionary mapping group names to lists of persons
            expenses: List of expense dictionaries
            prepayments: List of prepayment dictionaries
        """
        # Initialize with default values if not provided
        self.persons = persons or []
        self.groups = groups or {}
        self.expenses = expenses or []
        self.prepayments = prepayments or []
        
    @classmethod
    def create_with_defaults(cls):
        """Create an instance with default example data.
        
        Returns:
            ExpenseManager: An instance initialized with sample data
        """
        default_persons = ["Tobias", "Teal", "Adrian", "Patrick", "Marius", "Micha", "Jan", "Marlon"]
        default_groups = {
            "Alle": default_persons[:],
            "Fahrgemeinschaft": ["Tobias", "Teal", "Adrian", "Patrick", "Marius"]
        }
        default_expenses = [
            {"person": "Tobias", "amount": 1300, "group": "Alle", "subject": "Unterkunft"},
            {"person": "Teal", "amount": 1000, "group": "Fahrgemeinschaft", "subject": "Mietwagen"},
            {"person": "Marlon", "amount": 700, "group": "Alle", "subject": "Kaufland"},
            {"person": "Patrick", "amount": 450, "group": "Alle", "subject": "Bierdronka"},
            {"person": "Marius", "amount": 40, "group": "Alle", "subject": "Saunaholz"},
        ]
        default_prepayments = [
            {"person": "Adrian", "amount": 100, "recipient": "Tobias"},
            {"person": "Patrick", "amount": 100, "recipient": "Tobias"},
            {"person": "Marius", "amount": 100, "recipient": "Tobias"},
            {"person": "Micha", "amount": 100, "recipient": "Tobias"},
            {"person": "Jan", "amount": 100, "recipient": "Tobias"},
        ]
        return cls(default_persons[:], {k: v[:] for k, v in default_groups.items()}, 
                 default_expenses[:], default_prepayments[:])

    @classmethod
    def load_from_file(cls, filename):
        """Load data from a JSON file.
        
        Args:
            filename: Path to the JSON file to load
            
        Returns:
            ExpenseManager: An instance initialized with data from the file or defaults if file not found
        """
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                saved_data = json.load(f)
            return cls(
                saved_data["persons"],
                {k: v for k, v in saved_data["groups"].items()},
                saved_data["expenses"],
                saved_data["prepayments"]
            )
        return cls.create_with_defaults()
    
    def save_to_file(self, filename):
        """Save data to a JSON file.
        
        Args:
            filename: Path where to save the JSON file
        """
        data = {
            "persons": self.persons,
            "groups": self.groups,
            "expenses": self.expenses,
            "prepayments": self.prepayments
        }
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    
    def add_person(self, person, group=None):
        """Add a person to the list and optionally to a group.
        
        Args:
            person: Name of the person to add
            group: Optional group name to add the person to
        """
        if person not in self.persons:
            self.persons.append(person)
        if group and group in self.groups and person not in self.groups[group]:
            self.groups[group].append(person)
    
    def remove_person_from_group(self, person, group):
        """Remove a person from a group.
        
        If the person is not in any group after removal, they will also be
        removed from the persons list.
        
        Args:
            person: Name of the person to remove
            group: Group name to remove the person from
        """
        if group in self.groups and person in self.groups[group]:
            self.groups[group].remove(person)
            # If the person is not in any group anymore, remove from persons list
            if not any(person in members for members in self.groups.values()):
                self.persons.remove(person)
    
    def add_or_update_expense(self, person, amount, group, subject, index=None):
        """Add a new expense or update an existing one at the given index.
        
        Args:
            person: Name of the person who paid
            amount: Amount paid
            group: Name of the group to split the expense among
            subject: Description of what the expense was for
            index: Optional index for updating an existing expense
        """
        expense = {"person": person, "amount": amount, "group": group, "subject": subject}
        if index is not None and 0 <= index < len(self.expenses):
            self.expenses[index] = expense
        else:
            self.expenses.append(expense)
    
    def remove_expense(self, index):
        """Remove an expense at the given index.
        
        Args:
            index: Index of the expense to remove
        """
        if 0 <= index < len(self.expenses):
            del self.expenses[index]
    
    def add_or_update_prepayment(self, person, amount, recipient, index=None):
        """Add a new prepayment or update an existing one at the given index.
        
        Args:
            person: Name of the person who paid
            amount: Amount paid
            recipient: Name of the person who received the payment
            index: Optional index for updating an existing prepayment
        """
        prepayment = {"person": person, "amount": amount, "recipient": recipient}
        if index is not None and 0 <= index < len(self.prepayments):
            self.prepayments[index] = prepayment
        else:
            self.prepayments.append(prepayment)
    
    def remove_prepayment(self, index):
        """Remove a prepayment at the given index.
        
        Args:
            index: Index of the prepayment to remove
        """
        if 0 <= index < len(self.prepayments):
            del self.prepayments[index]
    
    def rename_group(self, old_name, new_name):
        """Rename a group and update all references to it.
        
        Args:
            old_name: Original name of the group
            new_name: New name for the group
        """
        if old_name in self.groups and new_name and new_name not in self.groups:
            self.groups[new_name] = self.groups.pop(old_name)
            for expense in self.expenses:
                if expense["group"] == old_name:
                    expense["group"] = new_name
    
    def calculate_balances(self):
        """Calculate what each person paid, owes, and their final balance.
        
        Returns:
            dict: Dictionary containing paid, received, owed amounts and final balances
        """
        paid = defaultdict(float)
        received = defaultdict(float)
        owes = defaultdict(float)
        
        # Process expenses
        for expense in self.expenses:
            person = expense["person"]
            amount = expense["amount"]
            group = self.groups[expense["group"]]
            
            paid[person] += amount
            per_person = amount / len(group)
            for member in group:
                owes[member] += per_person
        
        # Process prepayments
        for prepayment in self.prepayments:
            person = prepayment["person"]
            amount = prepayment["amount"]
            recipient = prepayment["recipient"]
            
            paid[person] += amount
            received[recipient] += amount
        
        # Calculate balance for each person
        balance = {person: paid.get(person, 0) - received.get(person, 0) - owes.get(person, 0) 
                  for person in self.persons}
        
        return {
            "paid": paid,
            "received": received,
            "owes": owes,
            "balance": balance
        }
    
    def calculate_transactions(self):
        """Calculate the optimal transactions to settle debts.
        
        Returns:
            dict: Dictionary containing balances and optimal transactions
        """
        balances = self.calculate_balances()
        balance = balances["balance"]
        
        creditors = [(p, b) for p, b in balance.items() if b > 0]
        debtors = [(p, -b) for p, b in balance.items() if b < 0]
        
        transactions = []
        i, j = 0, 0
        while i < len(creditors) and j < len(debtors):
            creditor, credit = creditors[i]
            debtor, debt = debtors[j]
            amount = min(credit, debt)
            
            if amount > 0:
                transactions.append({
                    "from": debtor,
                    "to": creditor,
                    "amount": amount
                })
            
            creditors[i] = (creditor, credit - amount)
            debtors[j] = (debtor, debt - amount)
            
            if creditors[i][1] <= 0:
                i += 1
            if debtors[j][1] <= 0:
                j += 1
        
        return {
            "balances": balances,
            "transactions": transactions
        }
    
    def get_summary(self):
        """Generate a text summary of expenses, prepayments, and calculations.
        
        Returns:
            str: Formatted summary text
        """
        summary = []
        
        # Expenses summary
        summary.append("Ausgangspunkt der Reisekostenaufteilung:")
        summary.append("\nAusgaben:")
        for expense in self.expenses:
            group_name = expense["group"]
            summary.append(f"- {expense['person']} hat {expense['amount']:.2f} € für {expense['subject']} ausgegeben, "
                         f"aufgeteilt auf die Gruppe '{group_name}' ({len(self.groups[group_name])} Personen).")
        
        # Prepayments summary
        summary.append("\nAnzahlungen:")
        for prepayment in self.prepayments:
            summary.append(f"- {prepayment['person']} hat {prepayment['amount']:.2f} € als Anzahlung an {prepayment['recipient']} gezahlt.")
        
        summary.append("\n" + "="*60)
        
        # Calculated transactions
        results = self.calculate_transactions()
        balances = results["balances"]
        transactions = results["transactions"]
        
        summary.append("\nTransaktionen die jetzt folgen müssen:")
        for trans in transactions:
            summary.append(f"{trans['from']} zahlt {trans['to']} {trans['amount']:.2f} €")
        
        # Verification summary
        paid = balances["paid"]
        received = balances["received"]
        owes = balances["owes"]
        balance = balances["balance"]
        
        summary.append("\nÜberprüfung der Kosten aus Sicht jeder Person:")
        for person in sorted(self.persons):
            total_owes = owes.get(person, 0)
            total_paid = paid.get(person, 0)
            total_received = received.get(person, 0)
            expected = balance.get(person, 0)
            label = "Erwartet" if expected >= 0 else "Schuldet"
            value = expected if expected >= 0 else -expected
            summary.append(f"{person}: Geschuldet {total_owes:.2f} €, Bezahlt {total_paid:.2f} €, "
                         f"Erhielt {total_received:.2f} €, {label} {value:.2f} €")
        
        return "\n".join(summary) 