# SitBuddy - Modern Babysitting Connection Platform

| UWA ID    | Name            | GitHub Username |
|-----------|-----------------|-----------------|
| 24728174  | Christine Oen   | christineoen    |
| 24351499  | DongSheng Li    | BenjaninLi-uw   |
| 24320547  | Huilin Tang     | KaylinTang      |
| 22860294  | Xin Chang       | XinChang-wa     |

## Overview

SitBuddy connects parents with qualified babysitters in Perth, Australia. Parents can search for babysitters, create bookings, and communicate through an integrated messaging system. Babysitters can manage their availability, accept or reject requests, and build a rated profile.

**Key Capabilities:**
- Smart babysitter search with location and availability filters
- Seamless booking system with real-time status updates  
- Integrated messaging for parent-babysitter communication
- Rating and review system for quality assurance
- Interactive maps for location-based matching
- Fully responsive design for mobile and desktop

---

## Tech Stack

- **Backend**: Flask (Python) with SQLAlchemy ORM
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5
- **Authentication**: Flask-Login
- **Security**: Flask-WTF CSRF protection
- **Maps**: Leaflet.js with OpenStreetMap tiles
- **Geocoding**: Nominatim (OpenStreetMap) — postcode and suburb lookup

---

## Setup

### Prerequisites
- Python 3.8+
- pip

### Install

```bash
git clone https://github.com/christineoen/CITS5505-Group-Project.git
cd CITS5505-Group-Project

python -m venv venv           # You may use python3 if command python is not found.
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
source venv/bin/activate     # Windows: venv\Scripts\activate
python app.py                # Alternative command: python3 app.py
```

Access at: http://127.0.0.1:5000

---

## Testing

```bash
source venv/bin/activate     # Windows: venv\Scripts\activate
python -m pytest             # Alternative command: python3 -m pytest
```

---

## Project Structure

```text
SitBuddy/
├── app.py                   # Flask application entry point
├── seed.py                  # Seeds users, bookings, messages, and ratings
├── seed_messages.py         # Booking/message/rating seed logic (called by seed.py)
├── dev.sh                   # Reset database, reseed, and start app
├── requirements.txt         # Python dependencies
├── utils.py                 
├── forms.py                 
├── __init__.py              
├── .gitignore               
├── .mailmap                 # Git author mapping
├── models/                  # Database models
│   ├── __init__.py          
│   ├── user.py              
│   ├── booking.py           
│   ├── message.py           
│   ├── rating.py            
│   ├── parent_profile.py    
│   └── babysitter_profile.py 
├── routes/                  # Flask blueprints
│   ├── __init__.py
│   ├── auth.py              # Authentication (login, signup, profile setup)
│   ├── main.py              # Main routes (home, profiles, bookings)
│   └── messages.py          # Messaging API endpoints
├── templates/               # Jinja2 HTML templates
│   ├── base.html            
│   ├── index.html           
│   ├── booking.html         # Booking creation form
│   ├── bookings.html        # Booking management dashboard
│   ├── messages.html        
│   ├── babysitter_profile.html 
│   ├── parent_profile.html  
│   ├── auth/                # Authentication templates
│   │   ├── login.html       
│   │   ├── signup.html      
│   │   ├── setup_profile.html # Role selection after signup
│   │   ├── setup_parent.html  # Parent profile setup
│   │   └── setup_sitter.html  # Babysitter profile setup
│   └── partials/            
│       ├── home_logged_out.html 
│       ├── navbar_auth.html 
│       └── navbar_guest.html 
├── static/                  
│   ├── css/
│   │   └── style.css        # Main stylesheet with responsive design
│   ├── js/                  # Client-side JavaScript
│   │   ├── index.js         # Homepage functionality (search, filters)
│   │   ├── booking.js       # Booking form validation and submission
│   │   ├── messages.js      # Messaging interface
│   │   ├── profiles.js      # Profile management
│   │   ├── rating.js        # Rating submission
│   │   ├── profile-map.js   # Interactive map for location display
│   │   ├── parent-profile.js # Parent-specific profile features
│   │   ├── setup-role.js    # Role selection logic
│   │   └── navbar-unread.js # Unread message notifications
│   ├── images/              
│   │   ├── SitBuddy_icon.png # Logo
│   │   ├── poster1.png       # Marketing images
│   │   ├── poster2.png
│   │   └── poster3.png
│   └── uploads/             # User-uploaded files
│       └── seed/            # Seed data profile photos (20 sample avatars)
│           ├── alice.jpg, ava.jpg, ben.jpg, chloe.jpg
│           ├── daniel.jpg, emma.jpg, ethan.jpg, grace.jpg
│           ├── henry.jpg, isla.jpg, jack.jpg, james.jpg
│           ├── liam.jpg, lucy.jpg, mia.jpg, noah.jpg
│           ├── oliver.jpg, sarah.jpg, sofia.jpg, tom.jpg
├── tests/                   # Test suite
│   ├── __init__.py
│   ├── conftest.py          # Shared pytest fixtures and test configuration
│   ├── test_auth.py         # Authentication and postcode lookup
│   ├── test_home.py         # Homepage and listing
│   ├── test_bookings.py     # Booking creation and state transition
│   ├── test_messages.py     # Messaging API
│   ├── test_profiles.py     # Profile view and edit
│   └── test_ratings.py      # Rating submission
├── instance/                
│   └── database.db          
├── planning/                
│   ├── Project Overview.txt 
│   └── user_stories.txt     
├── .vscode/                 
│   └── settings.json        
├── .github/                 
│   └── workflows/
│       └── test.yml         # CI: runs pytest on every push and PR
└── venv/                    # Python virtual environment
```

---

## License & Acknowledgments

Developed as part of **CITS5505 Agile Web Development** at the **University of Western Australia**.

This application acknowledges that its development takes place on Noongar land, and that Noongar people remain the spiritual and cultural custodians of their land.

**Third-party resources**: Bootstrap 5, Leaflet.js, OpenStreetMap (map tiles), Nominatim (geocoding API), Google Fonts (Inter, Playfair Display), Flask-SQLAlchemy, Flask-Login, Flask-WTF, pytest
