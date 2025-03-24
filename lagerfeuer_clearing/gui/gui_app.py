#!/usr/bin/env python3
"""
Graphical user interface for expense sharing calculations.
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from lagerfeuer_clearing.core import ExpenseManager

# Default save file location
SAVE_FILE = "expense_data.json"


class ExpenseApp:
    """GUI application for expense sharing calculations."""

    def __init__(self, root, manager):
        """Initialize the GUI application.

        Args:
            root: The tkinter root widget
            manager: An ExpenseManager instance
        """
        self.root = root
        self.root.title("Reisekostenaufteilung")
        self.manager = manager

        # Create shortcuts to manager data
        self.persons = manager.persons
        self.groups = manager.groups
        self.expenses = manager.expenses
        self.prepayments = manager.prepayments

        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(pady=10, expand=True)

        # Create tab frames
        self.group_frame = ttk.Frame(self.notebook)
        self.expense_frame = ttk.Frame(self.notebook)
        self.prepayment_frame = ttk.Frame(self.notebook)
        self.result_frame = ttk.Frame(self.notebook)

        # Add tabs to notebook
        self.notebook.add(self.group_frame, text="Gruppen")
        self.notebook.add(self.expense_frame, text="Ausgaben")
        self.notebook.add(self.prepayment_frame, text="Anzahlungen")
        self.notebook.add(self.result_frame, text="Ergebnisse")

        # Set up the tab content
        self.setup_group_tab()
        self.setup_expense_tab()
        self.setup_prepayment_tab()
        self.setup_result_tab()

    def update_all_comboboxes(self):
        """Update all comboboxes with current data."""
        self.group_combo["values"] = list(self.groups.keys())
        self.exp_person_combo["values"] = self.persons
        self.exp_group_combo["values"] = list(self.groups.keys())
        self.prepay_person_combo["values"] = self.persons
        self.prepay_recipient_combo["values"] = self.persons

    def setup_group_tab(self):
        """Set up the groups management tab."""
        ttk.Label(self.group_frame, text="Gruppen verwalten").grid(
            row=0, column=0, columnspan=2, pady=5
        )

        self.group_var = tk.StringVar()
        self.group_combo = ttk.Combobox(
            self.group_frame, textvariable=self.group_var, values=list(self.groups.keys())
        )
        self.group_combo.grid(row=1, column=0, padx=5)
        self.group_combo.bind("<<ComboboxSelected>>", self.update_group_list)

        self.group_listbox = tk.Listbox(self.group_frame, height=10)
        self.group_listbox.grid(row=2, column=0, rowspan=4, padx=5, pady=5)

        ttk.Label(self.group_frame, text="Person hinzufügen:").grid(row=1, column=1)
        self.person_var = tk.StringVar()
        ttk.Entry(self.group_frame, textvariable=self.person_var).grid(row=2, column=1, pady=5)
        ttk.Button(self.group_frame, text="Hinzufügen", command=self.add_person).grid(
            row=3, column=1
        )

        ttk.Button(self.group_frame, text="Löschen", command=self.remove_person).grid(
            row=4, column=1
        )

        ttk.Label(self.group_frame, text="Gruppe umbenennen:").grid(row=5, column=1)
        self.new_group_var = tk.StringVar()
        ttk.Entry(self.group_frame, textvariable=self.new_group_var).grid(row=6, column=1, pady=5)
        ttk.Button(self.group_frame, text="Umbenennen", command=self.rename_group).grid(
            row=7, column=1
        )

    def update_group_list(self, event=None):
        """Update the listbox with current group members."""
        self.group_listbox.delete(0, tk.END)
        selected_group = self.group_var.get()
        if selected_group in self.groups:
            for person in self.groups[selected_group]:
                self.group_listbox.insert(tk.END, person)

    def add_person(self):
        """Add a person to a group."""
        person = self.person_var.get().strip()
        group = self.group_var.get()
        if person and group in self.groups:
            self.manager.add_person(person, group)
            self.update_group_list()
            self.update_all_comboboxes()

    def remove_person(self):
        """Remove a person from a group."""
        group = self.group_var.get()
        selection = self.group_listbox.curselection()
        if selection and group in self.groups:
            person = self.group_listbox.get(selection[0])
            self.manager.remove_person_from_group(person, group)
            self.update_group_list()
            self.update_all_comboboxes()

    def rename_group(self):
        """Rename a group."""
        old_name = self.group_var.get()
        new_name = self.new_group_var.get().strip()
        if old_name in self.groups and new_name and new_name not in self.groups:
            self.manager.rename_group(old_name, new_name)
            self.group_var.set(new_name)
            self.update_group_list()
            self.update_all_comboboxes()

    def setup_expense_tab(self):
        """Set up the expenses management tab."""
        ttk.Label(self.expense_frame, text="Ausgaben verwalten").grid(
            row=0, column=0, columnspan=2, pady=5
        )

        self.expense_listbox = tk.Listbox(self.expense_frame, height=10, width=50)
        self.expense_listbox.grid(row=1, column=0, rowspan=4, padx=5, pady=5)
        self.expense_listbox.bind("<<ListboxSelect>>", self.load_expense)
        self.update_expense_list()

        ttk.Label(self.expense_frame, text="Person:").grid(row=1, column=1)
        self.exp_person_var = tk.StringVar()
        self.exp_person_combo = ttk.Combobox(
            self.expense_frame, textvariable=self.exp_person_var, values=self.persons
        )
        self.exp_person_combo.grid(row=2, column=1)

        ttk.Label(self.expense_frame, text="Betrag:").grid(row=3, column=1)
        self.exp_amount_var = tk.StringVar()
        ttk.Entry(self.expense_frame, textvariable=self.exp_amount_var).grid(row=4, column=1)

        ttk.Label(self.expense_frame, text="Gruppe:").grid(row=5, column=1)
        self.exp_group_var = tk.StringVar()
        self.exp_group_combo = ttk.Combobox(
            self.expense_frame, textvariable=self.exp_group_var, values=list(self.groups.keys())
        )
        self.exp_group_combo.grid(row=6, column=1)

        ttk.Label(self.expense_frame, text="Betreff:").grid(row=7, column=1)
        self.exp_subject_var = tk.StringVar()
        ttk.Entry(self.expense_frame, textvariable=self.exp_subject_var).grid(row=8, column=1)

        ttk.Button(self.expense_frame, text="Hinzufügen", command=self.add_expense).grid(
            row=9, column=1
        )
        ttk.Button(self.expense_frame, text="Übernehmen", command=self.update_expense).grid(
            row=10, column=1
        )
        ttk.Button(self.expense_frame, text="Löschen", command=self.remove_expense).grid(
            row=11, column=1
        )

    def update_expense_list(self):
        """Update the expense listbox with current expenses."""
        self.expense_listbox.delete(0, tk.END)
        for exp in self.expenses:
            self.expense_listbox.insert(
                tk.END, f"{exp['person']} - {exp['amount']} € - {exp['group']} - {exp['subject']}"
            )

    def load_expense(self, event):
        """Load an expense from the listbox into the input fields."""
        selection = self.expense_listbox.curselection()
        if selection:
            index = selection[0]
            exp = self.expenses[index]
            self.exp_person_var.set(exp["person"])
            self.exp_amount_var.set(str(exp["amount"]))
            self.exp_group_var.set(exp["group"])
            self.exp_subject_var.set(exp["subject"])

    def add_expense(self):
        """Add a new expense."""
        person = self.exp_person_var.get()
        try:
            amount = float(self.exp_amount_var.get() or 0)
        except ValueError:
            messagebox.showerror("Fehler", "Bitte einen gültigen Betrag eingeben.")
            return
        group = self.exp_group_var.get()
        subject = self.exp_subject_var.get().strip()
        if person in self.persons and group in self.groups and amount > 0 and subject:
            self.manager.add_or_update_expense(person, amount, group, subject)
            self.update_expense_list()
            # Clear fields after adding
            self.exp_person_var.set("")
            self.exp_amount_var.set("")
            self.exp_group_var.set("")
            self.exp_subject_var.set("")
            self.expense_listbox.selection_clear(0, tk.END)  # Clear selection

    def update_expense(self):
        """Update an existing expense."""
        selection = self.expense_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warnung", "Bitte wählen Sie einen Eintrag zum Bearbeiten aus.")
            return
        index = selection[0]
        person = self.exp_person_var.get()
        try:
            amount = float(self.exp_amount_var.get() or 0)
        except ValueError:
            messagebox.showerror("Fehler", "Bitte einen gültigen Betrag eingeben.")
            return
        group = self.exp_group_var.get()
        subject = self.exp_subject_var.get().strip()
        if person in self.persons and group in self.groups and amount > 0 and subject:
            self.manager.add_or_update_expense(person, amount, group, subject, index)
            self.update_expense_list()

    def remove_expense(self):
        """Remove an expense."""
        selection = self.expense_listbox.curselection()
        if selection:
            self.manager.remove_expense(selection[0])
            self.update_expense_list()

    def setup_prepayment_tab(self):
        """Set up the prepayments management tab."""
        ttk.Label(self.prepayment_frame, text="Anzahlungen verwalten").grid(
            row=0, column=0, columnspan=2, pady=5
        )

        self.prepay_listbox = tk.Listbox(self.prepayment_frame, height=10, width=50)
        self.prepay_listbox.grid(row=1, column=0, rowspan=4, padx=5, pady=5)
        self.prepay_listbox.bind("<<ListboxSelect>>", self.load_prepayment)
        self.update_prepay_list()

        ttk.Label(self.prepayment_frame, text="Person:").grid(row=1, column=1)
        self.prepay_person_var = tk.StringVar()
        self.prepay_person_combo = ttk.Combobox(
            self.prepayment_frame, textvariable=self.prepay_person_var, values=self.persons
        )
        self.prepay_person_combo.grid(row=2, column=1)

        ttk.Label(self.prepayment_frame, text="Betrag:").grid(row=3, column=1)
        self.prepay_amount_var = tk.StringVar()
        ttk.Entry(self.prepayment_frame, textvariable=self.prepay_amount_var).grid(row=4, column=1)

        ttk.Label(self.prepayment_frame, text="Empfänger:").grid(row=5, column=1)
        self.prepay_recipient_var = tk.StringVar()
        self.prepay_recipient_combo = ttk.Combobox(
            self.prepayment_frame, textvariable=self.prepay_recipient_var, values=self.persons
        )
        self.prepay_recipient_combo.grid(row=6, column=1)

        ttk.Button(self.prepayment_frame, text="Hinzufügen", command=self.add_prepayment).grid(
            row=7, column=1
        )
        ttk.Button(self.prepayment_frame, text="Übernehmen", command=self.update_prepayment).grid(
            row=8, column=1
        )
        ttk.Button(self.prepayment_frame, text="Löschen", command=self.remove_prepayment).grid(
            row=9, column=1
        )

    def update_prepay_list(self):
        """Update the prepayment listbox with current prepayments."""
        self.prepay_listbox.delete(0, tk.END)
        for prep in self.prepayments:
            self.prepay_listbox.insert(
                tk.END, f"{prep['person']} -> {prep['recipient']} : {prep['amount']} €"
            )

    def load_prepayment(self, event):
        """Load a prepayment from the listbox into the input fields."""
        selection = self.prepay_listbox.curselection()
        if selection:
            index = selection[0]
            prep = self.prepayments[index]
            self.prepay_person_var.set(prep["person"])
            self.prepay_amount_var.set(str(prep["amount"]))
            self.prepay_recipient_var.set(prep["recipient"])

    def add_prepayment(self):
        """Add a new prepayment."""
        person = self.prepay_person_var.get()
        try:
            amount = float(self.prepay_amount_var.get() or 0)
        except ValueError:
            messagebox.showerror("Fehler", "Bitte einen gültigen Betrag eingeben.")
            return
        recipient = self.prepay_recipient_var.get()
        if person in self.persons and recipient in self.persons and amount > 0:
            self.manager.add_or_update_prepayment(person, amount, recipient)
            self.update_prepay_list()
            # Clear fields after adding
            self.prepay_person_var.set("")
            self.prepay_amount_var.set("")
            self.prepay_recipient_var.set("")
            self.prepay_listbox.selection_clear(0, tk.END)  # Clear selection

    def update_prepayment(self):
        """Update an existing prepayment."""
        selection = self.prepay_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warnung", "Bitte wählen Sie einen Eintrag zum Bearbeiten aus.")
            return
        index = selection[0]
        person = self.prepay_person_var.get()
        try:
            amount = float(self.prepay_amount_var.get() or 0)
        except ValueError:
            messagebox.showerror("Fehler", "Bitte einen gültigen Betrag eingeben.")
            return
        recipient = self.prepay_recipient_var.get()
        if person in self.persons and recipient in self.persons and amount > 0:
            self.manager.add_or_update_prepayment(person, amount, recipient, index)
            self.update_prepay_list()

    def remove_prepayment(self):
        """Remove a prepayment."""
        selection = self.prepay_listbox.curselection()
        if selection:
            self.manager.remove_prepayment(selection[0])
            self.update_prepay_list()

    def setup_result_tab(self):
        """Set up the results tab."""
        ttk.Button(
            self.result_frame, text="Berechnung aktualisieren", command=self.calculate_results
        ).grid(row=0, column=0, pady=5)
        ttk.Button(self.result_frame, text="Als Text speichern", command=self.save_results).grid(
            row=0, column=1, pady=5, padx=5
        )
        ttk.Button(self.result_frame, text="Speichern", command=self.save_current_data).grid(
            row=0, column=2, pady=5, padx=5
        )

        scrollbar = ttk.Scrollbar(self.result_frame, orient="vertical")
        self.result_text = tk.Text(
            self.result_frame, height=20, width=80, yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.result_text.yview)
        self.result_text.grid(row=1, column=0, columnspan=3, padx=5, pady=5)
        scrollbar.grid(row=1, column=3, sticky="ns")

    def calculate_results(self):
        """Calculate and display results."""
        self.result_text.delete(1.0, tk.END)
        summary = self.manager.get_summary()
        self.result_text.insert(tk.END, summary)

    def save_results(self):
        """Save results to a text file."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(self.result_text.get(1.0, tk.END))
            messagebox.showinfo("Erfolg", f"Ergebnisse wurden in {file_path} gespeichert.")

    def save_current_data(self):
        """Save current data to the default save file."""
        self.manager.save_to_file(SAVE_FILE)
        messagebox.showinfo(
            "Erfolg", "Aktuelle Daten wurden gespeichert und werden beim nächsten Start geladen."
        )


def main():
    """Run the GUI application."""
    # Initialize the expense manager
    if os.path.exists(SAVE_FILE):
        manager = ExpenseManager.load_from_file(SAVE_FILE)
    else:
        manager = ExpenseManager.create_with_defaults()

    # Start the GUI application
    root = tk.Tk()
    # Create app instance but no need to store it since it modifies root directly
    ExpenseApp(root, manager)  # App instance is bound to root
    root.mainloop()


if __name__ == "__main__":
    main()
