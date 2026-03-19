from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)
DATA_FILE = 'data.json'
app.jinja_env.globals['enumerate'] = enumerate


def load_data():
    if not os.path.exists(DATA_FILE):
        return {'people': [], 'expenses': [], 'payments': []}
    data = json.load(open(DATA_FILE))
    if 'payments' not in data:
        data['payments'] = []
    return data


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

    for payment in data.get('payments', []):
        balances[payment['from']] += payment['amount']
        balances[payment['to']] -= payment['amount']

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
    date = request.form['date'].strip()
    payer = request.form['payer']
    try:
        total = float(request.form['total'])
    except ValueError:
        return redirect(url_for('index'))

    included = [p for p in data['people'] if request.form.get(f'include_{p}') == 'on']
    if not included:
        return redirect(url_for('index'))

    split_amount = round(total / len(included), 2)
    # Adjust for rounding so splits sum exactly to total
    splits = {p: split_amount for p in included}
    diff = round(total - sum(splits.values()), 2)
    if diff:
        splits[included[0]] = round(splits[included[0]] + diff, 2)

    if description and payer:
        data['expenses'].append({
            'description': description,
            'date': date,
            'payer': payer,
            'splits': splits
        })
        save_data(data)
    return redirect(url_for('index'))


@app.route('/mark_paid', methods=['POST'])
def mark_paid():
    data = load_data()
    from_person = request.form['from']
    to_person = request.form['to']
    try:
        amount = float(request.form['amount'])
    except ValueError:
        return redirect(url_for('index'))
    data['payments'].append({'from': from_person, 'to': to_person, 'amount': amount})
    save_data(data)
    return redirect(url_for('index'))


@app.route('/edit_expense/<int:index>', methods=['POST'])
def edit_expense(index):
    data = load_data()
    if 0 <= index < len(data['expenses']):
        description = request.form['description'].strip()
        date = request.form['date'].strip()
        payer = request.form['payer']
        try:
            total = float(request.form['total'])
        except ValueError:
            return redirect(url_for('index'))

        included = [p for p in data['people'] if request.form.get(f'include_{p}') == 'on']
        if not included:
            return redirect(url_for('index'))

        split_amount = round(total / len(included), 2)
        splits = {p: split_amount for p in included}
        diff = round(total - sum(splits.values()), 2)
        if diff:
            splits[included[0]] = round(splits[included[0]] + diff, 2)

        data['expenses'][index] = {
            'description': description,
            'date': date,
            'payer': payer,
            'splits': splits
        }
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
    app.run(host='0.0.0.0', debug=True)
