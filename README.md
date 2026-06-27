# 💸 BillSplit — Smart Bill Splitter with Settlement Tracker

A web-based bill splitting app with a smart debt simplification algorithm.
No login required for group members — just share a link!

---

## ✨ Features

- 👥 Create groups with a shareable UUID link
- 🙋 Members join by just entering their name (no account needed)
- 💰 Anyone in the group can add their own expenses
- ⚖️ Equal or custom splits per expense
- 📸 Payment proof — upload screenshot, mark as cash, or no proof
- 💸 Personal IOU tracking — record when someone lends money personally
- 🧮 Smart algorithm that calculates minimum transactions to settle all debts
- 📊 Real-time balance display per member
- 📱 Mobile-friendly responsive design

---

## ⚙️ Setup (Local)

### 1. Install dependencies
pip install -r requirements.txt

### 2. Create .env file
Create a .env file in the same folder as manage.py and add:

SECRET_KEY=your-secret-key-anything-random
DB_PASSWORD=your_mysql_password

### 3. Create MySQL database
Open MySQL Workbench or terminal and run:

CREATE DATABASE billsplit_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

### 4. Run migrations
python manage.py makemigrations
python manage.py migrate

### 5. Start the server
python manage.py runserver

Visit: http://127.0.0.1:8000

---

## 🔄 How to Use

### Step 1 — Create a Group
- Open the app
- Enter group name (e.g. Goa Trip)
- Enter your name
- Select currency
- Click Create Group

### Step 2 — Share the Link
- Click the Copy Link button
- Send the link to your friends on WhatsApp
- Friends open the link, enter their name and join
- No login or signup needed for anyone

### Step 3 — Add Expenses
- Click + Add Expense
- Select who paid
- Enter amount and title
- Choose equal or custom split
- Attach payment proof (screenshot, cash, or none)
- Click Add Expense

### Step 4 — Record Personal IOUs
- Click + Record Personal IOU
- Select who lent and who borrowed
- Enter amount and reason
- Attach proof if needed
- IOU is automatically included in final settlement

### Step 5 — Settle Up
- View the Settle Up section
- App shows minimum payments needed
- Example: Rahul pays Rs.500 to Priya

---

## 🧠 How the Algorithm Works

The debt simplification algorithm works in 3 steps:

1. Calculate net balance for each member (total paid minus total owed)
2. Separate into creditors (positive balance) and debtors (negative balance)
3. Greedy matching — pair the largest debtor with the largest creditor until all settled

This minimizes the number of transactions needed.
Example: 5 people with 10 expenses typically need only 4 payments
instead of many back-and-forth transfers.

---

## 💸 Personal IOU Feature

Record when someone lends money personally — not a group expense.

Example scenario:
Your friend forgot their wallet. You paid Rs.800 for their new footwear.
Add an IOU — it gets automatically included in the final settlement.
Your friend does not need to add a separate expense.

---

## 📸 Payment Proof Feature

When adding an expense or IOU, attach proof:

- No Proof — trust based, no attachment
- Paid in Cash — marks it as physical cash payment
- Upload Screenshot — attach GPay, PhonePe, Paytm, or bank screenshot

Proof is visible to all group members with a colored badge on each expense.

---

## 🗂️ Project Structure

billsplit/
├── .env                         your local secrets, never goes to GitHub
├── .gitignore
├── manage.py
├── Procfile                     for Railway deployment
├── requirements.txt
├── README.md
├── billsplit/                   Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── core/                        Main app
    ├── models.py                Group, Member, Expense, ExpenseSplit, IOU, Settlement
    ├── views.py                 All page logic
    ├── utils.py                 Debt simplification algorithm
    ├── urls.py
    ├── admin.py
    ├── apps.py
    ├── templates/
    │   └── core/
    │       ├── base.html
    │       ├── home.html
    │       ├── group_detail.html
    │       ├── add_expense.html
    │       ├── add_iou.html
    │       └── view_proof.html
    └── static/
        └── core/
            ├── css/
            │   └── style.css
            └── js/
                └── app.js

---

## 🚀 Deployment on Railway

### Step 1
Push your code to GitHub

### Step 2
Go to railway.app and login with GitHub

### Step 3
Click New Project and select Deploy from GitHub repo
Select your billsplit repository

### Step 4
Add MySQL database:
Click New inside your project
Click Database
Click Add MySQL

### Step 5
Add environment variables in your service Variables tab:
SECRET_KEY = any long random string
DEBUG = False

### Step 6
Set start command in Settings tab:
python manage.py migrate && python manage.py collectstatic --noinput && gunicorn billsplit.wsgi

### Step 7
Go to Settings and click Generate Domain
You get a public URL like:
https://billsplit-production.up.railway.app

Share this with anyone in the world!

---

## 🛠️ Built With

- Python 3.11
- Django 6.0
- MySQL
- HTML5, CSS3, JavaScript
- Pillow for image uploads
- Whitenoise for static files
- Deployed on Railway

---

## 📦 Requirements

Django>=4.2
mysqlclient>=2.1
Pillow>=10.0
gunicorn
dj-database-url
whitenoise
python-dotenv

---

## 👤 Author

Made by Nikita
Ahmedabad, Gujarat, India

GitHub: github.com/Nikita0625

---

## 📝 License

This project is open source and free to use.