# CITS5505 Group Project - SitBuddy

## Purpose

SitBuddy is a web application that connects parents with babysitters in their local area.

Parents can browse babysitter profiles, compare availability and experience, send booking requests, and communicate through an integrated messaging system. Babysitters can create a profile showcasing their skills and credentials, manage incoming booking requests, and engage in real-time conversations with parents.

The application is built with a client-server architecture using Flask on the backend, SQLite for data persistence via SQLAlchemy, and Bootstrap for the frontend. Users must register and log in to access the platform, and all user data is persisted between sessions.

### Key Features
- 👤 **User Authentication**: Secure login and registration system
- 🔍 **Profile Browsing**: Search and filter babysitters by location and availability
- 💬 **Messaging System**: Real-time communication between parents and babysitters
- 📅 **Booking Management**: Create, accept, and manage babysitting bookings
- 🎨 **Responsive Design**: Mobile-friendly interface using Bootstrap 5

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

### Seeding Message Data

To create sample bookings and messages for testing the messaging system:

```bash
python seed_messages.py
```

This will create:
- Multiple bookings with different statuses (pending, accepted, completed)
- Sample conversations between parents and babysitters
- Test messages for each booking

**Note**: Run `seed.py` first before running `seed_messages.py`.

---

## Messaging System

SitBuddy includes a comprehensive messaging system that enables communication between parents and babysitters.

### Features
- 💬 **Conversation Management**: View all conversations in one place
- 📨 **Real-time Messaging**: Send and receive messages instantly
- 🔔 **Unread Notifications**: Track unread message counts
- ✅ **Booking Actions**: Accept or reject bookings directly from messages
- 🎨 **Beautiful UI**: Clean, intuitive interface with message bubbles

### Quick Start
1. Login as a parent or babysitter
2. Click "Messages" in the navigation bar
3. Select a conversation to view messages
4. Type and send messages
5. (Babysitters only) Accept or reject pending bookings

### Documentation
For detailed information about the messaging system:
- 📖 **Complete Guide**: `消息系统完整指南.md` - Overview and navigation
- ⚡ **Quick Start**: `QUICK_START_MESSAGES.md` - Get started in 5 minutes
- 📚 **Full Documentation**: `MESSAGE_SYSTEM_README.md` - Detailed features and API
- 🏗️ **Architecture**: `ARCHITECTURE.md` - System design and data flow
- 🎬 **Demo Guide**: `DEMO_GUIDE.md` - Presentation and demonstration guide

### Testing the Messaging System
```bash
# Test the API endpoints
python test_messages_api.py

# Check database contents
python test_messages_api.py db
```

---

## Running the Tests

```bash
# Ensure the virtual environment is active
source venv/bin/activate      # Windows: venv\Scripts\activate

# Run the test suite
python -m pytest
```
