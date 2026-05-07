# SitBuddy - Modern Babysitting Connection Platform

| UWA ID    | Name            | GitHub Username |
|-----------|-----------------|-----------------|
| 24728174  | Christine Oen   | Christineoen    |
| 24351499  | DongSheng Li    | BenjaninLi-uw   |
| 24320547  | Huilin Tang     | KaylinTang      |
| 22860294  | Xin Chang       | XinChang-wa     |

## Overview

SitBuddy is a modern, elegant web application that connects parents with qualified babysitters in Perth, Australia. Featuring a sophisticated Morandi color palette and comprehensive messaging system, SitBuddy makes finding and booking childcare simple, secure, and visually appealing.

### ✨ Key Features
- 👤 **User Authentication**: Secure registration and login system with role-based access
- 🔍 **Smart Profile Management**: Detailed profiles with location-based matching
- 💬 **Real-time Messaging**: Enhanced communication system with booking management
- 📅 **Intelligent Booking System**: Create, manage, and track babysitting requests
- 🎨 **Modern Design**: Morandi color scheme with responsive, mobile-first interface
- 🗺️ **Location Integration**: Map-based babysitter discovery and filtering
- 🔒 **Enterprise Security**: CSRF protection, secure data handling, and input validation
- 📱 **Progressive Web App**: Optimized for all devices with app-like experience

### 🎨 Design Highlights
- **Morandi Color Palette**: Sophisticated sage green, dusty rose, and warm gray tones
- **Typography**: Inter and Playfair Display fonts for modern, elegant text
- **Interactive Elements**: Smooth animations and hover effects
- **Photo Carousel**: Dynamic image showcase with ChatGPT-generated visuals
- **Responsive Navigation**: Adaptive layout for desktop, tablet, and mobile

---

## 🛠️ Technology Stack

- **Backend**: Flask (Python) with SQLAlchemy ORM
- **Database**: SQLite with comprehensive data modeling
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Styling**: Bootstrap 5 + Custom Morandi CSS Framework
- **Fonts**: Inter (modern sans-serif) + Playfair Display (elegant serif)
- **Authentication**: Flask-Login with session management
- **Security**: Flask-WTF CSRF Protection + Input validation
- **Maps**: Leaflet.js for interactive location features
- **Icons**: Custom SVG icon system

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Modern web browser (Chrome, Firefox, Safari, Edge)

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

🌐 **Access the application**: http://127.0.0.1:5000

### 🎯 Demo Accounts
All seeded accounts use password: `password123`
- **Parents**: Browse babysitters, create bookings, send messages
- **Babysitters**: Manage availability, accept/reject bookings, communicate with families

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

## 💬 Enhanced Messaging System

### 🌟 Advanced Features
- **Conversation Management**: Organized, searchable conversation list
- **Real-time Updates**: Instant message delivery with optimistic UI updates
- **Role-based Interface**: Tailored experiences for parents and babysitters
- **Booking Integration**: Accept/reject bookings directly from chat interface
- **System Notifications**: Automated status updates and confirmations
- **Unread Tracking**: Visual indicators and message counters
- **Mobile Optimization**: Touch-friendly interface with responsive design
- **Message History**: Persistent conversation storage and retrieval
- **Timezone Support**: Accurate timestamp handling across time zones

### 👥 User Experience

#### 👨‍👩‍👧‍👦 Parents (Booking Creators)
- **Dashboard View**: Overview of all active conversations and booking statuses
- **Message Sending**: Rich text communication with babysitters
- **Status Monitoring**: Real-time updates on booking request progress
- **History Access**: Complete conversation and booking history

#### 👶 Babysitters (Service Providers)
- **Request Management**: Accept or reject bookings with one-click actions
- **Communication Tools**: Professional messaging interface
- **Status Updates**: Automatic system message generation
- **Availability Control**: Manage booking preferences and schedules

### 🔧 Technical Implementation

#### API Endpoints
| Endpoint | Method | Description | Response |
|----------|--------|-------------|----------|
| `/messages/` | GET | Main messaging interface | HTML page |
| `/messages/api/conversations` | GET | Get all user conversations | JSON array |
| `/messages/api/conversation/<id>` | GET | Get specific conversation messages | JSON object |
| `/messages/api/send` | POST | Send new message | JSON confirmation |
| `/messages/api/booking/<id>/status` | PUT | Update booking status | JSON status |

#### Security Features
- **CSRF Protection**: All forms protected against cross-site request forgery
- **Input Validation**: Server-side validation for all message content
- **Authentication**: Session-based user verification
- **Authorization**: Role-based access control for booking actions

## 🧪 Testing & Quality Assurance

### Automated Testing
```bash
# Activate virtual environment
source venv/bin/activate

# Run comprehensive test suite
python -m pytest

# Test messaging system specifically
python test_messages_api.py

# Database integrity check
python test_messages_api.py db
```

### Manual Testing Checklist
- ✅ User registration and authentication
- ✅ Profile creation and editing
- ✅ Booking creation and management
- ✅ Real-time messaging functionality
- ✅ Mobile responsiveness
- ✅ Cross-browser compatibility
- ✅ Security and input validation

---

## 📁 Project Architecture

```
SitBuddy/
├── 📄 app.py                    # Flask application entry point
├── 📄 requirements.txt          # Python dependencies
├── 📄 seed.py                   # User data seeding script
├── 📄 seed_messages.py          # Message data seeding script
├── 📄 test_messages_api.py      # API testing utilities
├── 📄 utils.py                  # Helper functions and utilities
├── 📄 forms.py                  # WTForms form definitions
├── 📂 models/                   # Database models (SQLAlchemy)
│   ├── 📄 __init__.py
│   ├── 📄 user.py              # User authentication model
│   ├── 📄 message.py           # Messaging system model
│   ├── 📄 booking.py           # Booking management model
│   ├── 📄 parent_profile.py    # Parent profile model
│   └── 📄 babysitter_profile.py # Babysitter profile model
├── 📂 routes/                   # Flask route handlers
│   ├── 📄 auth.py              # Authentication routes
│   ├── 📄 main.py              # Main application routes
│   └── 📄 messages.py          # Messaging system routes
├── 📂 templates/                # Jinja2 HTML templates
│   ├── 📄 base.html            # Base template with navigation
│   ├── 📄 index.html           # Homepage with hero section
│   ├── 📄 messages.html        # Messaging interface
│   ├── 📂 auth/                # Authentication templates
│   └── 📂 partials/            # Reusable template components
├── 📂 static/                   # Static assets
│   ├── 📂 css/
│   │   └── 📄 style.css        # Morandi-themed custom styles
│   ├── 📂 js/
│   │   ├── 📄 messages.js      # Real-time messaging functionality
│   │   ├── 📄 index.js         # Homepage interactions
│   │   └── 📄 *.js             # Feature-specific scripts
│   └── 📂 images/              # Application images and icons
│       ├── 📄 SitBuddy_icon.png # Application logo/favicon
│       ├── 📄 poster1.png      # Hero carousel image 1
│       ├── 📄 poster2.png      # Hero carousel image 2
│       └── 📄 poster3.png      # Hero carousel image 3
├── 📂 instance/                 # Instance-specific files
│   └── 📄 database.db          # SQLite database file
└── 📂 planning/                 # Project documentation
    ├── 📄 Project Overview.txt  # High-level project description
    └── 📄 user_stories.txt      # User requirements and stories
```

---

## 🎨 Design System & UI/UX

### Morandi Color Palette
```css
--sage: #9CAF88           /* Primary brand color */
--dusty-rose: #D4A5A5     /* Accent color */
--warm-gray: #B8A99A      /* Secondary elements */
--soft-blue: #A8C4D6      /* Information highlights */
--muted-lavender: #C4B5D6 /* Subtle accents */
--pale-terracotta: #D6B5A8 /* Warm highlights */
--cream: #F5F3F0          /* Background base */
--charcoal: #4A4A4A       /* Text primary */
```

### Typography Hierarchy
- **Headlines**: Playfair Display (elegant serif)
- **Body Text**: Inter (modern sans-serif)
- **UI Elements**: Inter (consistent interface)

### Component Library
- **Hero Section**: Dynamic carousel with artistic typography
- **Feature Cards**: Hover animations with Morandi backgrounds
- **Navigation**: Responsive with enhanced mobile icon sizing
- **Messaging Interface**: Real-time chat with role-based styling
- **Forms**: Rounded inputs with sage green focus states
- **Buttons**: Consistent styling across all interaction points

---

## 🚀 Development & Deployment

### Development Workflow
```bash
# Set up development environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run in development mode
export FLASK_ENV=development
python app.py

# Watch for file changes (optional)
# Use nodemon or similar tool for auto-restart
```

### Code Quality Standards
- **Python**: PEP 8 compliance with meaningful naming
- **JavaScript**: ES6+ features with consistent formatting
- **CSS**: BEM methodology for class naming
- **HTML**: Semantic markup with accessibility considerations
- **Documentation**: Comprehensive docstrings and comments

### Performance Optimizations
- **Image Optimization**: Compressed PNG files for web delivery
- **CSS Minification**: Production-ready stylesheets
- **JavaScript Bundling**: Efficient script loading
- **Database Indexing**: Optimized queries for messaging system
- **Caching Strategy**: Static asset caching headers

---

## 🤝 Contributing

We welcome contributions to SitBuddy! Please follow these guidelines:

### Development Process
1. **Fork** the repository to your GitHub account
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request with detailed description

### Contribution Guidelines
- Follow existing code style and conventions
- Add tests for new functionality
- Update documentation as needed
- Ensure all tests pass before submitting
- Use meaningful commit messages

### Areas for Contribution
- 🐛 Bug fixes and improvements
- ✨ New features and enhancements
- 📚 Documentation updates
- 🎨 UI/UX improvements
- 🔧 Performance optimizations
- 🧪 Test coverage expansion

---

## 📄 License & Acknowledgments

### Academic License
This project is developed as part of **CITS5505 Agile Web Development** coursework at the **University of Western Australia**. 

### Acknowledgments
- **Course Instructor**: CITS5505 teaching team
- **Design Inspiration**: Morandi color palette and modern web design principles
- **Image Generation**: ChatGPT-generated carousel images
- **Land Acknowledgment**: This application acknowledges that its development takes place on Noongar land, and that Noongar people remain the spiritual and cultural custodians of their land.

### Third-Party Resources
- **Bootstrap 5**: Responsive framework foundation
- **Leaflet.js**: Interactive mapping functionality
- **Google Fonts**: Inter and Playfair Display typography
- **Flask Ecosystem**: SQLAlchemy, WTF, Login extensions

---

## 📞 Support & Contact

### Getting Help
- 📖 **Documentation**: Check the `planning/` directory for detailed specifications
- 🐛 **Issues**: Report bugs via GitHub Issues
- 💡 **Feature Requests**: Submit enhancement ideas through GitHub
- 📧 **Academic Inquiries**: Contact through UWA channels

### Development Team
For project-related questions or collaboration opportunities, please reach out to any team member listed at the top of this README.

---

## 🔮 Future Roadmap

### Planned Enhancements
- 🔔 **Push Notifications**: Real-time alerts for mobile devices
- 💳 **Payment Integration**: Secure payment processing
- ⭐ **Review System**: Rating and feedback functionality
- 📊 **Analytics Dashboard**: Usage insights and metrics
- 🌐 **Multi-language Support**: Internationalization features
- 🔐 **Advanced Security**: Two-factor authentication
- 📱 **Mobile App**: Native iOS and Android applications

### Technical Improvements
- **Database Migration**: PostgreSQL for production scalability
- **Caching Layer**: Redis for improved performance
- **API Documentation**: OpenAPI/Swagger integration
- **Monitoring**: Application performance monitoring
- **CI/CD Pipeline**: Automated testing and deployment

---

*Built with ❤️ by the SitBuddy team at the University of Western Australia*
