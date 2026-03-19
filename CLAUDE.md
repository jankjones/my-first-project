# Expense Splitter — Project Overview

## Stack
- **Backend:** Python 3.9, Flask
- **Frontend:** HTML, CSS, vanilla JavaScript
- **Data storage:** `data.json` (local file, no database)

## Project Structure
```
my-first-project/
├── app.py                  # Flask backend, all routes and logic
├── data.json               # Persistent data (auto-created on first run)
├── templates/
│   └── index.html          # Single-page frontend
└── CLAUDE.md
```

## Running the App
```
cd ~/my-first-project
python3 app.py
```
Then open **http://127.0.0.1:5000** in a browser.

## Data Model
`data.json` contains three keys:
- `people` — list of names
- `expenses` — list of expense objects: `description`, `date`, `payer`, `splits` (dict of person → amount)
- `payments` — list of payment objects: `from`, `to`, `amount`

## Key Features
- Add/remove people
- Add expenses with a description, date, total cost, payer, and even split (with per-person checkboxes to exclude)
- Inline edit form for expenses
- Settlement calculation (who owes who and how much)
- Mark debts as paid

## Key Logic
- **Splits:** Even split among checked people; rounding remainder assigned to first person
- **Settlements:** Calculated dynamically from balances derived from expenses minus payments
- `enumerate` is registered as a Jinja2 global to support `enumerate()` in templates

## GitHub
- Remote: `git@github.com:jankjones/my-first-project.git`
- Branch: `main`
