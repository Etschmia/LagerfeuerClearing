import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from collections import defaultdict
import json
import os

# Initiale Standard-Vorgabewerte (Fallback)
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

SAVE_FILE = "expense_data.json"

if os.path.exists(SAVE_FILE):
    with open(SAVE_FILE, "r", encoding="utf-8") as f:
        saved_data = json.load(f)
    persons = saved_data["persons"]
    groups = {k: v for k, v in saved_data["groups"].items()}
    expenses = saved_data["expenses"]
    prepayments = saved_data["prepayments"]
else:
    persons = default_persons[:]
    groups = {k: v[:] for k, v in default_groups.items()}
    expenses = default_expenses[:]
    prepayments = default_prepayments[:]

class ExpenseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Reisekostenaufteilung")
        
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(pady=10, expand=True)
        
        self.group_frame = ttk.Frame(self.notebook)
        self.expense_frame = ttk.Frame(self.notebook)
        self.prepayment_frame = ttk.Frame(self.notebook)
        self.result_frame = ttk.Frame(self.notebook)
        
        self.notebook.add(self.group_frame, text="Gruppen")
        self.notebook.add(self.expense_frame, text="Ausgaben")
        self.notebook.add(self.prepayment_frame, text="Anzahlungen")
        self.notebook.add(self.result_frame, text="Ergebnisse")
        
        self.setup_group_tab()
        self.setup_expense_tab()
        self.setup_prepayment_tab()
        self.setup_result_tab()

    def update_all_comboboxes(self):
        self.group_combo['values'] = list(groups.keys())
        self.exp_person_combo['values'] = persons
        self.exp_group_combo['values'] = list(groups.keys())
        self.prepay_person_combo['values'] = persons
        self.prepay_recipient_combo['values'] = persons

    def setup_group_tab(self):
        ttk.Label(self.group_frame, text="Gruppen verwalten").grid(row=0, column=0, columnspan=2, pady=5)
        
        self.group_var = tk.StringVar()
        self.group_combo = ttk.Combobox(self.group_frame, textvariable=self.group_var, values=list(groups.keys()))
        self.group_combo.grid(row=1, column=0, padx=5)
        self.group_combo.bind("<<ComboboxSelected>>", self.update_group_list)
        
        self.group_listbox = tk.Listbox(self.group_frame, height=10)
        self.group_listbox.grid(row=2, column=0, rowspan=4, padx=5, pady=5)
        
        ttk.Label(self.group_frame, text="Person hinzufügen:").grid(row=1, column=1)
        self.person_var = tk.StringVar()
        ttk.Entry(self.group_frame, textvariable=self.person_var).grid(row=2, column=1, pady=5)
        ttk.Button(self.group_frame, text="Hinzufügen", command=self.add_person).grid(row=3, column=1)
        
        ttk.Button(self.group_frame, text="Löschen", command=self.remove_person).grid(row=4, column=1)
        
        ttk.Label(self.group_frame, text="Gruppe umbenennen:").grid(row=5, column=1)
        self.new_group_var = tk.StringVar()
        ttk.Entry(self.group_frame, textvariable=self.new_group_var).grid(row=6, column=1, pady=5)
        ttk.Button(self.group_frame, text="Umbenennen", command=self.rename_group).grid(row=7, column=1)

    def update_group_list(self, event=None):
        self.group_listbox.delete(0, tk.END)
        selected_group = self.group_var.get()
        if selected_group in groups:
            for person in groups[selected_group]:
                self.group_listbox.insert(tk.END, person)

    def add_person(self):
        person = self.person_var.get().strip()
        group = self.group_var.get()
        if person and group in groups:
            if person not in persons:
                persons.append(person)
            if person not in groups[group]:
                groups[group].append(person)
            self.update_group_list()
            self.update_all_comboboxes()

    def remove_person(self):
        group = self.group_var.get()
        selection = self.group_listbox.curselection()
        if selection and group in groups:
            person = self.group_listbox.get(selection[0])
            groups[group].remove(person)
            if not any(person in members for members in groups.values()):
                persons.remove(person)
            self.update_group_list()
            self.update_all_comboboxes()

    def rename_group(self):
        old_name = self.group_var.get()
        new_name = self.new_group_var.get().strip()
        if old_name in groups and new_name and new_name not in groups:
            groups[new_name] = groups.pop(old_name)
            for expense in expenses:
                if expense["group"] == old_name:
                    expense["group"] = new_name
            self.group_var.set(new_name)
            self.update_group_list()
            self.update_all_comboboxes()

    def setup_expense_tab(self):
        ttk.Label(self.expense_frame, text="Ausgaben verwalten").grid(row=0, column=0, columnspan=2, pady=5)
        
        self.expense_listbox = tk.Listbox(self.expense_frame, height=10, width=50)
        self.expense_listbox.grid(row=1, column=0, rowspan=4, padx=5, pady=5)
        self.expense_listbox.bind("<<ListboxSelect>>", self.load_expense)
        self.update_expense_list()
        
        ttk.Label(self.expense_frame, text="Person:").grid(row=1, column=1)
        self.exp_person_var = tk.StringVar()
        self.exp_person_combo = ttk.Combobox(self.expense_frame, textvariable=self.exp_person_var, values=persons)
        self.exp_person_combo.grid(row=2, column=1)
        
        ttk.Label(self.expense_frame, text="Betrag:").grid(row=3, column=1)
        self.exp_amount_var = tk.StringVar()
        ttk.Entry(self.expense_frame, textvariable=self.exp_amount_var).grid(row=4, column=1)
        
        ttk.Label(self.expense_frame, text="Gruppe:").grid(row=5, column=1)
        self.exp_group_var = tk.StringVar()
        self.exp_group_combo = ttk.Combobox(self.expense_frame, textvariable=self.exp_group_var, values=list(groups.keys()))
        self.exp_group_combo.grid(row=6, column=1)
        
        ttk.Label(self.expense_frame, text="Betreff:").grid(row=7, column=1)
        self.exp_subject_var = tk.StringVar()
        ttk.Entry(self.expense_frame, textvariable=self.exp_subject_var).grid(row=8, column=1)
        
        ttk.Button(self.expense_frame, text="Hinzufügen", command=self.add_expense).grid(row=9, column=1)
        ttk.Button(self.expense_frame, text="Übernehmen", command=self.update_expense).grid(row=10, column=1)
        ttk.Button(self.expense_frame, text="Löschen", command=self.remove_expense).grid(row=11, column=1)

    def update_expense_list(self):
        self.expense_listbox.delete(0, tk.END)
        for exp in expenses:
            self.expense_listbox.insert(tk.END, f"{exp['person']} - {exp['amount']} € - {exp['group']} - {exp['subject']}")

    def load_expense(self, event):
        selection = self.expense_listbox.curselection()
        if selection:
            index = selection[0]
            exp = expenses[index]
            self.exp_person_var.set(exp["person"])
            self.exp_amount_var.set(str(exp["amount"]))
            self.exp_group_var.set(exp["group"])
            self.exp_subject_var.set(exp["subject"])

    def add_expense(self):
        person = self.exp_person_var.get()
        try:
            amount = float(self.exp_amount_var.get() or 0)
        except ValueError:
            messagebox.showerror("Fehler", "Bitte einen gültigen Betrag eingeben.")
            return
        group = self.exp_group_var.get()
        subject = self.exp_subject_var.get().strip()
        if person in persons and group in groups and amount > 0 and subject:
            expenses.append({"person": person, "amount": amount, "group": group, "subject": subject})
            self.update_expense_list()
            # Felder nach Hinzufügen leeren
            self.exp_person_var.set("")
            self.exp_amount_var.set("")
            self.exp_group_var.set("")
            self.exp_subject_var.set("")
            self.expense_listbox.selection_clear(0, tk.END)  # Auswahl aufheben

    def update_expense(self):
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
        if person in persons and group in groups and amount > 0 and subject:
            expenses[index] = {"person": person, "amount": amount, "group": group, "subject": subject}
            self.update_expense_list()

    def remove_expense(self):
        selection = self.expense_listbox.curselection()
        if selection:
            del expenses[selection[0]]
            self.update_expense_list()

    def setup_prepayment_tab(self):
        ttk.Label(self.prepayment_frame, text="Anzahlungen verwalten").grid(row=0, column=0, columnspan=2, pady=5)
        
        self.prepay_listbox = tk.Listbox(self.prepayment_frame, height=10, width=50)
        self.prepay_listbox.grid(row=1, column=0, rowspan=4, padx=5, pady=5)
        self.prepay_listbox.bind("<<ListboxSelect>>", self.load_prepayment)
        self.update_prepay_list()
        
        ttk.Label(self.prepayment_frame, text="Person:").grid(row=1, column=1)
        self.prepay_person_var = tk.StringVar()
        self.prepay_person_combo = ttk.Combobox(self.prepayment_frame, textvariable=self.prepay_person_var, values=persons)
        self.prepay_person_combo.grid(row=2, column=1)
        
        ttk.Label(self.prepayment_frame, text="Betrag:").grid(row=3, column=1)
        self.prepay_amount_var = tk.StringVar()
        ttk.Entry(self.prepayment_frame, textvariable=self.prepay_amount_var).grid(row=4, column=1)
        
        ttk.Label(self.prepayment_frame, text="Empfänger:").grid(row=5, column=1)
        self.prepay_recipient_var = tk.StringVar()
        self.prepay_recipient_combo = ttk.Combobox(self.prepayment_frame, textvariable=self.prepay_recipient_var, values=persons)
        self.prepay_recipient_combo.grid(row=6, column=1)
        
        ttk.Button(self.prepayment_frame, text="Hinzufügen", command=self.add_prepayment).grid(row=7, column=1)
        ttk.Button(self.prepayment_frame, text="Übernehmen", command=self.update_prepayment).grid(row=8, column=1)
        ttk.Button(self.prepayment_frame, text="Löschen", command=self.remove_prepayment).grid(row=9, column=1)

    def update_prepay_list(self):
        self.prepay_listbox.delete(0, tk.END)
        for prep in prepayments:
            self.prepay_listbox.insert(tk.END, f"{prep['person']} -> {prep['recipient']} : {prep['amount']} €")

    def load_prepayment(self, event):
        selection = self.prepay_listbox.curselection()
        if selection:
            index = selection[0]
            prep = prepayments[index]
            self.prepay_person_var.set(prep["person"])
            self.prepay_amount_var.set(str(prep["amount"]))
            self.prepay_recipient_var.set(prep["recipient"])

    def add_prepayment(self):
        person = self.prepay_person_var.get()
        try:
            amount = float(self.prepay_amount_var.get() or 0)
        except ValueError:
            messagebox.showerror("Fehler", "Bitte einen gültigen Betrag eingeben.")
            return
        recipient = self.prepay_recipient_var.get()
        if person in persons and recipient in persons and amount > 0:
            prepayments.append({"person": person, "amount": amount, "recipient": recipient})
            self.update_prepay_list()
            # Felder nach Hinzufügen leeren
            self.prepay_person_var.set("")
            self.prepay_amount_var.set("")
            self.prepay_recipient_var.set("")
            self.prepay_listbox.selection_clear(0, tk.END)  # Auswahl aufheben

    def update_prepayment(self):
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
        if person in persons and recipient in persons and amount > 0:
            prepayments[index] = {"person": person, "amount": amount, "recipient": recipient}
            self.update_prepay_list()

    def remove_prepayment(self):
        selection = self.prepay_listbox.curselection()
        if selection:
            del prepayments[selection[0]]
            self.update_prepay_list()

    def setup_result_tab(self):
        ttk.Button(self.result_frame, text="Berechnung aktualisieren", command=self.calculate_results).grid(row=0, column=0, pady=5)
        ttk.Button(self.result_frame, text="Als Text speichern", command=self.save_results).grid(row=0, column=1, pady=5, padx=5)
        ttk.Button(self.result_frame, text="Speichern", command=self.save_current_data).grid(row=0, column=2, pady=5, padx=5)
        
        scrollbar = ttk.Scrollbar(self.result_frame, orient="vertical")
        self.result_text = tk.Text(self.result_frame, height=20, width=80, yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.result_text.yview)
        self.result_text.grid(row=1, column=0, columnspan=3, padx=5, pady=5)
        scrollbar.grid(row=1, column=3, sticky="ns")

    def calculate_results(self):
        self.result_text.delete(1.0, tk.END)
        
        self.result_text.insert(tk.END, "Ausgangspunkt der Reisekostenaufteilung:\n")
        self.result_text.insert(tk.END, "\nAusgaben:\n")
        for expense in expenses:
            self.result_text.insert(tk.END, f"- {expense['person']} hat {expense['amount']:.2f} € für {expense['subject']} ausgegeben, "
                                          f"aufgeteilt auf die Gruppe '{expense['group']}' ({len(groups[expense['group']])} Personen).\n")
        self.result_text.insert(tk.END, "\nAnzahlungen:\n")
        for prepayment in prepayments:
            self.result_text.insert(tk.END, f"- {prepayment['person']} hat {prepayment['amount']:.2f} € als Anzahlung an {prepayment['recipient']} gezahlt.\n")
        self.result_text.insert(tk.END, "\n" + "="*60 + "\n")
        
        paid = defaultdict(float)
        received = defaultdict(float)
        owes = defaultdict(float)

        for expense in expenses:
            person = expense["person"]
            amount = expense["amount"]
            group = groups[expense["group"]]
            paid[person] += amount
            per_person = amount / len(group)
            for member in group:
                owes[member] += per_person

        for prepayment in prepayments:
            person = prepayment["person"]
            amount = prepayment["amount"]
            recipient = prepayment["recipient"]
            paid[person] += amount
            received[recipient] += amount

        balance = {person: paid[person] - received[person] - owes[person] for person in persons}

        self.result_text.insert(tk.END, "\nTransaktionen die jetzt folgen müssen:\n")
        self.result_text.insert(tk.END, f"{'Schuldner':<15} {'Gläubiger':<15} {'Betrag':<10}\n")
        self.result_text.insert(tk.END, "-"*40 + "\n")
        creditors = [(p, b) for p, b in balance.items() if b > 0]
        debtors = [(p, -b) for p, b in balance.items() if b < 0]

        i, j = 0, 0
        while i < len(creditors) and j < len(debtors):
            creditor, credit = creditors[i]
            debtor, debt = debtors[j]
            amount = min(credit, debt)
            if amount > 0:
                self.result_text.insert(tk.END, f"{debtor:<15} {creditor:<15} {amount:>8.2f} €\n")
            creditors[i] = (creditor, credit - amount)
            debtors[j] = (debtor, debt - amount)
            if creditors[i][1] <= 0:
                i += 1
            if debtors[j][1] <= 0:
                j += 1

        self.result_text.insert(tk.END, "\nÜberprüfung der Kosten aus Sicht jeder Person:\n")
        self.result_text.insert(tk.END, f"{'Person':<15} {'Geschuldet':>12} {'Bezahlt':>12} {'Erhielt':>12} {'Bilanz':>12}\n")
        self.result_text.insert(tk.END, "-"*65 + "\n")
        for person in sorted(persons):
            total_owes = owes[person]
            total_paid = paid[person]
            total_received = received[person]
            expected = balance[person]
            label = "Erwartet" if expected >= 0 else "Schuldet"
            value = expected if expected >= 0 else -expected
            self.result_text.insert(tk.END, f"{person:<15} {total_owes:>12.2f} {total_paid:>12.2f} {total_received:>12.2f} {value:>12.2f} ({label})\n")

    def save_results(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(self.result_text.get(1.0, tk.END))
            messagebox.showinfo("Erfolg", f"Ergebnisse wurden in {file_path} gespeichert.")

    def save_current_data(self):
        data = {
            "persons": persons,
            "groups": groups,
            "expenses": expenses,
            "prepayments": prepayments
        }
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        messagebox.showinfo("Erfolg", "Aktuelle Daten wurden gespeichert und werden beim nächsten Start geladen.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseApp(root)
    root.mainloop()