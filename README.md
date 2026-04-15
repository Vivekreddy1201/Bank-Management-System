# SmartBank – Online Banking Management System

A full-stack banking web application built with **FastAPI** and **PostgreSQL**, supporting secure authentication, account management, transactions, and loan services through a clean modular architecture.

---

## Overview

SmartBank is a modern banking system that allows users to:

* Manage multiple bank accounts
* Perform secure financial transactions
* Apply and track loans
* View transaction history
* Authenticate securely using JWT cookies

The project demonstrates **scalable backend design**, **secure authentication**, and **clean separation of concerns**.

---

## Features

### Authentication

* User registration with email validation
* Secure login using **JWT stored in HTTP cookies**
* Protected routes using dependency injection
* Password update functionality
* Logout with cookie clearing

### Account Management

* Create multiple accounts (Savings / Current)
* View account details and balances
* Delete accounts with confirmation

### Transactions

* Deposit & Withdraw money
* Transfer funds between accounts
* View detailed transaction history

### Security

* Strong password validation (Pydantic)
* JWT verification on every request
* Ownership checks before operations
* Redirect unauthorized users to login

---

## Tech Stack

| Layer          | Technology         |
| -------------- | ------------------ |
| Backend        | FastAPI (Python)   |
| Database       | PostgreSQL         |
| DB Connector   | psycopg2           |
| Authentication | JWT (HTTP Cookies) |
| Validation     | Pydantic v2        |
| Frontend       | Jinja2 Templates   |
| Server         | Uvicorn            |

---

## Project Structure

```id="projstruct"
Bank-Management-System/
│
├── main.py
├── database.py
├── dependencies.py
├── models.py
├── schemas.py
├── templates_config.py
│
├── routers/
│   ├── auth.py
│   ├── dashboard.py
│   ├── bank.py
│   └── loans.py
│
├── services/
│   └── auth_service.py
│
├── frontend/
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── create_account.html
│   ├── delete_account.html
│   ├── confirm_delete.html
│   ├── deposit.html
│   ├── withdraw.html
│   ├── transfer.html
│   ├── transfer_balance.html
│   ├── transactions.html
│   ├── update_password.html
│   └── message.html
│
└── README.md
```

---

## API Modules

### Auth (`auth.py`)

* Login, Register, Logout
* Password update

### Dashboard (`dashboard.py`)

* User dashboard (protected)

### Banking (`bank.py`)

* Deposit, Withdraw, Transfer
* Account creation & deletion
* Transaction history

---

## Authentication Flow

* JWT stored in **HTTP cookie (`access_token`)**
* Verified using `get_current_user` dependency
* Invalid/missing token → redirected to login

---

## Database Design

**PostgreSQL** database with key tables:

* **users**
* **accounts**
* **transactions**

Uses `RealDictCursor` for dictionary-based query results.

---

## Setup Instructions

### 1. Clone Repository

```bash id="clone"
git clone https://github.com/Vivekreddy1201/Bank-Management-System.git
cd Bank-Management-System
```

### 2. Create Virtual Environment

```bash id="venv"
python -m venv venv
source venv/bin/activate
# Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash id="install"
pip install fastapi uvicorn psycopg2-binary "python-jose[cryptography]" "passlib[bcrypt]" "pydantic[email]" python-multipart jinja2
```

### 4. Setup PostgreSQL

```sql id="db"
CREATE DATABASE bank;
```

Update connection string in `database.py`:

```python id="conn"
postgresql://<user>:<password>@localhost:5432/bank
```

---

## Run the Application

```bash id="run"
uvicorn main:app --host 127.0.0.1 --port 5000 --reload
```

Open in browser:

```
http://127.0.0.1:5000
```

---

## Key Highlights

* Modular architecture (**routers + services**)
* Stateless authentication using **JWT cookies**
* Clean UI with reusable **base template (base.html)**
* Strong validation with **Pydantic v2**
  
