# CITS5505 Group Project - SitBuddy

## Purpose

SitBuddy is a web application that connects parents with babysitters in their local area.

Parents can browse babysitter profiles, compare availability and experience, send booking requests, and leave reviews. Babysitters can create a profile showcasing their skills and credentials, manage incoming booking requests, and build a reputation through reviews.

The application is built with a client-server architecture using Flask on the backend, SQLite for data persistence via SQLAlchemy, and Bootstrap for the frontend. Users must register and log in to access the platform, and all user data is persisted between sessions.

---

## Group Members

| UWA ID | Name | GitHub Username |
|--------|------|-----------------|
| TODO   | TODO | TODO            |
| TODO   | TODO | TODO            |
| TODO   | TODO | TODO            |
| TODO   | TODO | TODO            |

---

## Launch Instructions

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

The app will be available at http://127.0.0.1:5000.

---

## Seeding the Database

To populate the database with 10 sample babysitters and 10 sample parents:

```bash
python seed.py
```

All seed accounts use the password `password123`. Re-running the script is safe — existing accounts are skipped.

---

## Running the Tests

```bash
# Ensure the virtual environment is active
source venv/bin/activate      # Windows: venv\Scripts\activate

# Run the test suite
python -m pytest
```
