# SitBuddy - Babysitting Connection Platform

## Overview

SitBuddy is a modern web application that connects parents with qualified babysitters in their local area. Built with Flask and featuring a comprehensive messaging system, SitBuddy makes finding and booking childcare simple and secure.

### Key Features
- 👤 **User Authentication**: Secure registration and login system
- 🔍 **Profile Management**: Detailed profiles for both parents and babysitters
- 💬 **Real-time Messaging**: Enhanced communication system with booking management
- 📅 **Booking System**: Create, manage, and track babysitting requests
- 🎨 **Responsive Design**: Mobile-friendly interface using Bootstrap 5
- 🔒 **Security**: CSRF protection and secure data handling

---

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Styling**: Bootstrap 5
- **Authentication**: Flask-Login
- **Security**: Flask-WTF CSRF Protection

---

## Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd SitBuddy

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize the database and seed data
python seed.py
python seed_messages.py

# Run the application
python app.py
```

The application will be available at **http://127.0.0.1:5000**

---

## Database Setup

### Initial User Data
```bash
python seed.py
```
Creates 10 sample parents and 10 sample babysitters. All accounts use password: `password123`

### Messaging Test Data
```bash
python seed_messages.py
```
Creates sample bookings and conversations for testing the messaging system.

**Note**: Run `seed.py` before `seed_messages.py`

---

## Messaging System

### Features
- **Conversation Management**: Organized list of all conversations
- **Real-time Updates**: Messages appear instantly without page refresh
- **Role-based Interface**: Different views for parents and babysitters
- **Booking Actions**: Accept/reject bookings directly from chat
- **System Messages**: Automated notifications for booking status changes
- **Unread Tracking**: Visual indicators for new messages
- **Responsive Design**: Works seamlessly on mobile devices

### User Roles

#### Parents (Senders)
- View booking request status
- Send messages to babysitters
- Read-only interface for pending requests
- Receive notifications when bookings are accepted/rejected

#### Babysitters (Receivers)
- Accept or reject booking requests
- Send messages to parents
- Action buttons for pending requests
- Generate system messages for status changes

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/messages/` | GET | Main messaging interface |
| `/messages/api/conversations` | GET | Get all conversations |
| `/messages/api/conversation/<id>` | GET | Get specific conversation |
| `/messages/api/send` | POST | Send new message |
| `/messages/api/booking/<id>/status` | PUT | Update booking status |

### Testing the Messaging System

```bash
# Test API functionality
python test_messages_api.py

# Check database contents only
python test_messages_api.py db
```

---

## Project Structure

```
SitBuddy/
├── app.py                 # Main application file
├── requirements.txt       # Python dependencies
├── seed.py               # User data seeding
├── seed_messages.py      # Message data seeding
├── test_messages_api.py  # API testing script
├── models/               # Database models
│   ├── user.py
│   ├── message.py
│   ├── booking.py
│   └── ...
├── routes/               # Application routes
│   ├── auth.py
│   ├── main.py
│   └── messages.py
├── templates/            # HTML templates
│   ├── messages.html
│   └── ...
├── static/               # Static assets
│   ├── css/
│   └── js/
│       └── messages.js
└── planning/             # Project documentation
```

---

## Development

### Running Tests
```bash
# Activate virtual environment
source venv/bin/activate

# Run test suite
python -m pytest
```

### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Include docstrings for all functions and classes
- Maintain consistent indentation (4 spaces)

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## License

This project is developed as part of CITS5505 coursework at the University of Western Australia.

---

## Support

For issues or questions, please refer to the project documentation in the `planning/` directory or contact the development team.
