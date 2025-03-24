from collections import defaultdict

# Personen und Gruppen definieren
persons = ["Tobias", "Teal", "Adrian", "Patrick", "Marius", "Micha", "Jan", "Marlon"]
groups = {
    "Alle": persons,
    "Fahrgemeinschaft": ["Tobias", "Teal", "Adrian", "Patrick", "Marius"]
}

# Ausgaben definieren
expenses = [
    {"person": "Tobias", "amount": 1300, "group": "Alle", "subject": "Unterkunft"},
    {"person": "Teal", "amount": 1000, "group": "Fahrgemeinschaft", "subject": "Mietwagen"},
    {"person": "Marlon", "amount": 700, "group": "Alle", "subject": "Kaufland"},
    {"person": "Patrick", "amount": 450, "group": "Alle", "subject": "Bierdronka"},
    {"person": "Marius", "amount": 40, "group": "Alle", "subject": "Saunaholz"},
]

# Anzahlungen definieren
prepayments = [
    {"person": "Adrian", "amount": 100, "recipient": "Tobias"},
    {"person": "Patrick", "amount": 100, "recipient": "Tobias"},
    {"person": "Marius", "amount": 100, "recipient": "Tobias"},
    {"person": "Micha", "amount": 100, "recipient": "Tobias"},
    {"person": "Jan", "amount": 100, "recipient": "Tobias"},
]

# Ausgangspunkt in Worten ausgeben
print("Ausgangspunkt der Reisekostenaufteilung:")
print("\nAusgaben:")
for expense in expenses:
    print(f"- {expense['person']} hat {expense['amount']:.2f} € für {expense['subject']} ausgegeben, "
          f"aufgeteilt auf die Gruppe '{expense['group']}' ({len(groups[expense['group']])} Personen).")
print("\nAnzahlungen:")
for prepayment in prepayments:
    print(f"- {prepayment['person']} hat {prepayment['amount']:.2f} € als Anzahlung an {prepayment['recipient']} gezahlt.")
print("\n" + "="*60)

# Berechnung
paid = defaultdict(float)
received = defaultdict(float)
owes = defaultdict(float)

# Verarbeite Ausgaben
for expense in expenses:
    person = expense["person"]
    amount = expense["amount"]
    group = groups[expense["group"]]
    subject = expense["subject"]

    paid[person] += amount
    per_person = amount / len(group)
    for member in group:
        owes[member] += per_person

# Verarbeite Anzahlungen
for prepayment in prepayments:
    person = prepayment["person"]
    amount = prepayment["amount"]
    recipient = prepayment["recipient"]

    paid[person] += amount
    received[recipient] += amount

# Bilanz berechnen
balance = {person: paid[person] - received[person] - owes[person] for person in persons}

# Zahlungen minimieren
print("\nTransaktionen die jetzt folgen müssen:")
creditors = [(p, b) for p, b in balance.items() if b > 0]
debtors = [(p, -b) for p, b in balance.items() if b < 0]

i, j = 0, 0
while i < len(creditors) and j < len(debtors):
    creditor, credit = creditors[i]
    debtor, debt = debtors[j]
    amount = min(credit, debt)
    
    if amount > 0:
        print(f"{debtor} zahlt {creditor} {amount:.2f} €")
    
    creditors[i] = (creditor, credit - amount)
    debtors[j] = (debtor, debt - amount)
    
    if creditors[i][1] <= 0:
        i += 1
    if debtors[j][1] <= 0:
        j += 1

# Überprüfung mit dynamischer Bezeichnung
print("\nÜberprüfung der Kosten aus Sicht jeder Person:")
for person in persons:
    total_owes = owes[person]
    total_paid = paid[person]
    total_received = received[person]
    expected = balance[person]
    label = "Erwartet" if expected >= 0 else "Wird zahlen"
    value = expected if expected >= 0 else -expected  # Negativen Wert positiv darstellen
    print(f"{person}: Geschuldet {total_owes:.2f} €, Bezahlt {total_paid:.2f} €, "
          f"Erhielt {total_received:.2f} €, {label} {value:.2f} €")
