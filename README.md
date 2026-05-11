# SitBuddy - Modern Babysitting Connection Platform

| UWA ID    | Name            | GitHub Username |
|-----------|-----------------|-----------------|
| 24728174  | Christine Oen   | christineoen    |
| 24351499  | DongSheng Li    | BenjaninLi-uw   |
| 24320547  | Huilin Tang     | KaylinTang      |
| 22860294  | Xin Chang       | XinChang-wa     |

## Overview

SitBuddy connects parents with qualified babysitters in Perth, Australia. Parents can search for babysitters, create bookings, and communicate through an integrated messaging system. Babysitters can manage their availability, accept or reject requests, and build a rated profile.

---

## Tech Stack

- **Backend**: Flask (Python) with SQLAlchemy ORM
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5
- **Authentication**: Flask-Login
- **Security**: Flask-WTF CSRF protection
- **Maps**: Leaflet.js

---

## Setup

### Prerequisites
- Python 3.8+
- pip

### Install

```bash
git clone https://github.com/christineoen/CITS5505-Group-Project.git
cd CITS5505-Group-Project

python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### Database & Seed

Run once to create the database schema and populate it with sample data:

```bash
python seed.py
```

This creates 10 parents, 10 babysitters, sample bookings (past and upcoming), messages, and ratings.

To **reset and reseed** from scratch (wipes the database):

```bash
./dev.sh
```

`dev.sh` deletes the existing database, recreates the schema, reseeds all data, and then starts the app.

### Demo accounts

All seeded accounts use password: `password123`

| Role        | Sample email           |
|-------------|------------------------|
| Parent      | sarah@example.com      |
| Babysitter  | emma@example.com       |

---

## Running the App

```bash
source venv/bin/activate
python app.py
```

Access at: http://127.0.0.1:5000

---

## Testing

```bash
source venv/bin/activate
python -m pytest
```

---

## Project Structure

```
SitBuddy/
├── app.py                   # Flask application entry point
├── seed.py                  # Seeds users, bookings, messages, and ratings
├── seed_messages.py         # Booking/message/rating seed logic (called by seed.py)
├── dev.sh                   # Reset database, reseed, and start app
├── requirements.txt
├── utils.py
├── forms.py
├── models/
│   ├── user.py
│   ├── booking.py
│   ├── message.py
│   ├── rating.py
│   ├── parent_profile.py
│   └── babysitter_profile.py
├── routes/
│   ├── auth.py
│   ├── main.py
│   └── messages.py
├── templates/
└── static/
    ├── css/
    ├── js/
    └── images/
```

---

## License & Acknowledgments

Developed as part of **CITS5505 Agile Web Development** at the **University of Western Australia**.

This application acknowledges that its development takes place on Noongar land, and that Noongar people remain the spiritual and cultural custodians of their land.

**Third-party resources**: Bootstrap 5, Leaflet.js, Google Fonts (Inter, Playfair Display), Flask-SQLAlchemy, Flask-Login, Flask-WTF
