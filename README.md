# Local:Byte — Cafe Management & Online Ordering System

A full-stack Django-based cafe management and online ordering system built with Django, PostgreSQL, HTML, CSS, and JavaScript.

Local:Byte brings customer ordering, table reservations, order management, inventory management, kitchen stock monitoring, payments, and cafe administration into one centralized system.

## 🚀 Features

### 👤 Customer

* Browse menu without registration
* Browse food categories
* Add food items to cart
* Update cart quantities
* Remove items from cart
* Place food orders after login
* UPI / Card / Cash payment options
* View order history
* Track order status
* Book cafe tables
* View available tables
* Pay ₹500 reservation token
* View reservation invoice
* View reservation history
* Manage profile

### 🪑 Table Reservation

* Select reservation date
* Select reservation time
* Select number of guests
* View available tables
* Prevent duplicate table reservations
* ₹500 reservation token
* Reservation payment tracking
* Manager confirmation
* Reservation invoice generation

### 📦 Order Management

Customer order workflow:

```text
Place Order
    ↓
Pending
    ↓
Payment
    ↓
Manager Confirmation
    ↓
Confirmed
    ↓
Preparing
    ↓
Ready
    ↓
Completed
```

Orders cannot be confirmed by the manager until payment is completed.

### 👨‍💼 Manager

The Manager dashboard provides operational control over:

* Pending orders
* Confirmed orders
* Preparing orders
* Ready orders
* Completed orders
* Pending reservations
* Reservation confirmation
* Payment monitoring
* Customer monitoring
* Inventory monitoring
* Low-stock monitoring
* Kitchen stock
* Kitchen orders
* Stock transactions

### 👑 Admin

The Admin has complete system-level control including:

* User management
* Menu management
* Category management
* Table management
* Reservation management
* Order management
* Inventory management
* Payment management
* Cafe settings
* Customer management
* Analytics and reporting

Analytics are intentionally kept separate from the Manager dashboard.

### 🍳 Kitchen

The kitchen module provides a simple operational workflow:

```text
Confirmed
    ↓
Preparing
    ↓
Ready
    ↓
Completed
```

Kitchen Stock provides a basic view of:

* Ingredient/item name
* Available kitchen quantity
* Last updated time

The system does not automatically deduct ingredients based on recipes.

### 📊 Inventory

Inventory management includes:

* Inventory items
* Current quantity
* Units
* Minimum stock level
* Low-stock detection
* Purchase transactions
* Stock issue
* Consumption
* Stock adjustment
* Stock transactions
* Issue stock to kitchen

Inventory flow:

```text
Main Inventory
      ↓
Stock Issue
      ↓
Kitchen Stock
      ↓
Kitchen Dashboard
```

## 🛠️ Tech Stack

### Backend

* Python
* Django
* Django ORM
* PostgreSQL

### Frontend

* HTML
* CSS
* JavaScript
* Django Templates

### Development Tools

* Git
* GitHub
* pgAdmin
* Postman

## 🗂️ Project Structure

```text
cafe_management/
│
├── home/
│   ├── migrations/
│   ├── static/
│   │   └── home/
│   │       └── style.css
│   │
│   ├── templates/
│   │   └── home/
│   │
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   └── tests.py
│
├── mysite/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── manage.py
├── .gitignore
├── .env
└── README.md
```

> `.env` is intentionally excluded from GitHub through `.gitignore`.

## ⚙️ Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/HoDoR07/localbyte-cafe-management.git
cd localbyte-cafe-management
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

Windows:

```bash
.venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install django psycopg2-binary python-dotenv pillow
```

### 5. Configure environment variables

Create a `.env` file in the project root:

```env
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=5432
```

Never commit the `.env` file.

### 6. Run migrations

```bash
python manage.py migrate
```

### 7. Start the development server

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

## 🔐 Security

Sensitive configuration is stored using environment variables.

The following files are excluded from Git:

```text
.env
.venv/
db.sqlite3
media/
__pycache__/
*.pyc
```

Database credentials and secret configuration should never be committed to the repository.

## 📌 Project Status

The core Local:Byte cafe management and online ordering workflow has been implemented and tested, including:

* Customer ordering
* Cart management
* Online payment flow
* Cash payment workflow
* Order invoices
* Table reservations
* Reservation token payment
* Reservation invoices
* Manager confirmation
* Kitchen workflow
* Inventory management
* Kitchen stock
* Role-based access
* Admin management
* Operational dashboards

## 👨‍💻 Author

Raushan_Kumar
Built as a portfolio project using Django and PostgreSQL.
