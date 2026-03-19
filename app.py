from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)
DATA_FILE = 'data.json'
app.jinja_env.globals['enumerate'] = enumerate


def load_data():
    if not os.path.exists(DATA_FILE):
        return {'people': [], 'expenses': []}
    with open(DATA_FILE) as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)


def calculate_settlements(data):
    balances = {person: 0 for person in data['people']}

    for expense in data['expenses']:
        payer = expense['payer']
        splits = expense['splits']
        total = sum(splits.values())

        balances[payer] += total
        for person, amount in splits.items():
            balances[person] -= amount

    creditors = sorted([(p, b) for p, b in balances.items() if b > 0.01], key=lambda x: -x[1])
    debtors = sorted([(p, -b) for p, b in balances.items() if b < -0.01], key=lambda x: -x[1])

    settlements = []
    i, j = 0, 0
    while i < len(creditors) and j < len(debtors):
        creditor, credit = creditors[i]
        debtor, debt = debtors[j]
        amount = min(credit, debt)
        settlements.append({'from': debtor, 'to': creditor, 'amount': round(amount, 2)})
        creditors[i] = (creditor, credit - amount)
        debtors[j] = (debtor, debt - amount)
        if creditors[i][1] < 0.01:
            i += 1
        if debtors[j][1] < 0.01:
            j += 1

    return settlements


@app.route('/')
def index():
    data = load_data()
    settlements = calculate_settlements(data)
    return render_template('index.html', data=data, settlements=settlements)


@app.route('/add_person', methods=['POST'])
def add_person():
    data = load_data()
    name = request.form['name'].strip()
    if name and name not in data['people']:
        data['people'].append(name)
        save_data(data)
    return redirect(url_for('index'))


@app.route('/remove_person/<name>')
def remove_person(name):
    data = load_data()
    data['people'] = [p for p in data['people'] if p != name]
    save_data(data)
    return redirect(url_for('index'))


@app.route('/add_expense', methods=['POST'])
def add_expense():
    data = load_data()
    description = request.form['description'].strip()
    payer = request.form['payer']
    splits = {}
    for person in data['people']:
        val = request.form.get(f'split_{person}', '0').strip()
        try:
            amount = float(val)
        except ValueError:
            amount = 0
        if amount > 0:
            splits[person] = amount

    if description and payer and splits:
        data['expenses'].append({
            'description': description,
            'payer': payer,
            'splits': splits
        })
        save_data(data)
    return redirect(url_for('index'))


@app.route('/remove_expense/<int:index>')
def remove_expense(index):
    data = load_data()
    if 0 <= index < len(data['expenses']):
        data['expenses'].pop(index)
        save_data(data)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
