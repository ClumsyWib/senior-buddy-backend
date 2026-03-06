# Senior Buddy — Backend Setup Guide

---

## Before You Start

Make sure you have these installed on your computer:
- Python 3.x → https://www.python.org/downloads/
- MySQL → https://dev.mysql.com/downloads/installer/
- Git → https://git-scm.com/download/win

---

## Step 1 — Clone the repo

This downloads the project code to your computer.
Open a terminal and run:

```bash
git clone https://github.com/ClumsyWib/senior-buddy-backend.git
cd senior-buddy-backend
```

---

## Step 2 — Create a virtual environment

A virtual environment keeps project packages separate from your system Python.
Run this inside the project folder:

```bash
python -m venv venv
```

Then activate it (you need to do this every time you open the project):

```bash
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

You'll see (venv) appear at the start of your terminal line — that means it's active.

---

## Step 3 — Fix PowerShell script permission (Windows only)

If you get a "running scripts is disabled" error when activating venv, run this once:

```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then activate venv again.

---

## Step 4 — Install all packages

This installs Django and everything the project needs.
Make sure (venv) is active before running this:

```bash
pip install -r requirements.txt
```

---

## Step 5 — Set up MySQL database

Open MySQL Workbench or MySQL Command Line Client and run:

```sql
CREATE DATABASE senior_buddy_db;
```

Then run this to create the Role table data:

```sql
USE senior_buddy_db;
INSERT INTO Role (role_name) VALUES
('ADMIN'),('SENIOR'),('CAREGIVER'),('FAMILY'),('VOLUNTEER');
```

---

## Step 6 — Create your `.env` file

This file stores your MySQL password securely.
Create a new file called `.env` in the root project folder (same place as manage.py).
Add this line inside it:

```
DB_PASSWORD=your_mysql_password_here
```

Replace `your_mysql_password_here` with your actual MySQL root password.
This file is not uploaded to GitHub — each person creates their own.

---

## Step 7 — Run migrations

This creates all the database tables Django needs internally.
Make sure (venv) is active:

```bash
python manage.py migrate
```

---

## Step 8 — Load dummy data

This fills the database with test users and sample data so you can test everything:

```bash
python dummy_data.py
```

---

## Step 9 — Create a superuser

This creates your admin account to log into the admin panel:

```bash
python manage.py createsuperuser
```

Enter any email, username and password when asked.

---

## Step 10 — Run the server

```bash
python manage.py runserver
```

---

## Access Points

Once the server is running, open these in your browser:

| URL | What it is |
|---|---|
| http://127.0.0.1:8000/admin/ | Admin panel — manage all data here |
| http://127.0.0.1:8000/api/schema/swagger/ | API docs — all endpoints for Android |

---

## Test Credentials

These accounts are created by the dummy data script.
Password for all accounts: `test1234`

| Role | Email |
|---|---|
| Senior | s1@test.com |
| Caregiver | c1@test.com |
| Family | f1@test.com |
| Volunteer | v1@test.com |

---

## Every Time You Come Back to Work

Open terminal in the project folder and run:

```bash
venv\Scripts\activate        # activate virtual environment
python manage.py runserver   # start the server
```

---

## Pulling Latest Changes from GitHub

When someone pushes new code, run this to get their changes:

```bash
git pull
```

---

## Common Errors

**"No module named MySQLdb"**
Add these two lines at the very top of settings.py:
```python
import pymysql
pymysql.install_as_MySQLdb()
```

**"venv\Scripts\activate cannot be loaded"**
Run this once:
```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**"Table already exists" during migrate**
Run this instead:
```bash
python manage.py migrate --fake-initial
```

**Admin panel datetime error**
Make sure settings.py has:
```python
USE_TZ = False
```
