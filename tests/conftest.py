from datetime import date, time, datetime, timedelta

import pytest

from app import create_app
from models import db as _db
from models.user import User
from models.babysitter_profile import BabysitterProfile
from models.booking import Booking
from models.parent_profile import ParentProfile
from models.rating import Rating


@pytest.fixture
def app():
    application = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test-secret",
    })
    with application.app_context():
        _db.create_all()
        yield application
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_client(app, client):
    """Test client with a fresh user logged in (no role/profile yet)."""
    user = User(name="Test User", email="test@test.com")
    user.set_password("Password1!")
    _db.session.add(user)
    _db.session.commit()

    client.post("/auth/login", data={"email": "test@test.com", "password": "Password1!"})
    return client


@pytest.fixture
def parent_user(app):
    """A User with a ParentProfile, not logged in."""
    user = User(
        name="Parent User",
        email="parent@test.com",
        suburb="Nedlands",
        postcode="6009",
        latitude=-31.9829,
        longitude=115.8012,
    )
    user.set_password("Password1!")
    _db.session.add(user)
    _db.session.flush()
    _db.session.add(ParentProfile(user_id=user.id, children=[], about="Test family"))
    _db.session.commit()
    return user


@pytest.fixture
def sitter_user(app):
    """A User with a BabysitterProfile, not logged in."""
    user = User(
        name="Sitter User",
        email="sitter@test.com",
        suburb="Subiaco",
        postcode="6008",
        latitude=-31.9490,
        longitude=115.8270,
    )
    user.set_password("Password1!")
    _db.session.add(user)
    _db.session.flush()
    _db.session.add(BabysitterProfile(
        user_id=user.id,
        bio="Experienced sitter",
        hourly_rate=25.0,
        experience_years=3,
    ))
    _db.session.commit()
    return user


@pytest.fixture
def parent_client(app, client, parent_user):
    """Test client logged in as a parent."""
    client.post("/auth/login", data={"email": "parent@test.com", "password": "Password1!"})
    return client


@pytest.fixture
def sitter_client(app, client, sitter_user):
    """Test client logged in as a sitter."""
    client.post("/auth/login", data={"email": "sitter@test.com", "password": "Password1!"})
    return client


@pytest.fixture
def booking(app, parent_user, sitter_user):
    """A pending booking between parent_user and sitter_user."""
    b = Booking(
        parent_id=parent_user.parent_profile.id,
        babysitter_id=sitter_user.babysitter_profile.id,
        date=date(2026, 8, 1),
        start_time=time(18, 0),
        duration_hours=3,
        status="pending",
    )
    _db.session.add(b)
    _db.session.commit()
    return b


@pytest.fixture
def accepted_booking(app, parent_user, sitter_user):
    """An accepted booking between parent_user and sitter_user (future date)."""
    b = Booking(
        parent_id=parent_user.parent_profile.id,
        babysitter_id=sitter_user.babysitter_profile.id,
        date=date(2026, 8, 1),
        start_time=time(10, 0),
        duration_hours=2,
        status="accepted",
    )
    _db.session.add(b)
    _db.session.commit()
    return b


@pytest.fixture
def completed_booking(app, parent_user, sitter_user):
    """A completed booking between parent_user and sitter_user (past date)."""
    b = Booking(
        parent_id=parent_user.parent_profile.id,
        babysitter_id=sitter_user.babysitter_profile.id,
        date=date(2026, 1, 1),
        start_time=time(10, 0),
        duration_hours=2,
        status="completed",
    )
    _db.session.add(b)
    _db.session.commit()
    return b
