# 💸 BillSplit — Smart Bill Splitter with Settlement Tracker

A web-based bill splitting app with a smart debt simplification algorithm. No login required for group members — just share a link!

## Features
- Create groups with a shareable UUID link
- Members join by just entering their name (no account needed)
- Add expenses with equal or custom splits
- Smart algorithm that calculates minimum transactions to settle all debts
- Real-time balance display per member
- Mobile-friendly responsive design

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Create MySQL database
```sql
CREATE DATABASE billsplit_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. Update database credentials
Edit `billsplit/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'billsplit_db',
        'USER': 'your_mysql_username',
        'PASSWORD': 'your_mysql_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 4. Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Start the server
```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000

## How the Algorithm Works

The debt simplification algorithm works in 3 steps:

1. **Calculate net balance** for each member (total paid − total owed)
2. **Separate** into creditors (positive balance) and debtors (negative balance)
3. **Greedy matching** — pair the largest debtor with the largest creditor until all settled

This minimizes the number of transactions needed. For example, 5 people with 10 expenses
typically need only 4 payments instead of many back-and-forth transfers.

## Project Structure
```
billsplit/
├── billsplit/          Django project config
│   ├── settings.py
│   └── urls.py
└── core/               Main app
    ├── models.py       Group, Member, Expense, ExpenseSplit
    ├── views.py        All page logic
    ├── utils.py        Debt simplification algorithm
    ├── urls.py
    ├── templates/core/ HTML templates
    └── static/core/    CSS + JS
```
