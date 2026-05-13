# Tests for booking creation and state transitions
# Owner: bookings team member
#
# Areas to cover:
#   - POST /booking/<babysitter_id>: create a booking request
#   - Conflict detection (overlapping pending/accepted bookings)
#   - POST /bookings/<id>/accept: sitter accepts, overlapping pending bookings rejected
#   - POST /bookings/<id>/reject: sitter rejects
#   - POST /bookings/<id>/cancel: parent cancels pending booking
#   - POST /bookings/<id>/complete: parent marks completed after start time
#   - Non-owners cannot act on each other's bookings (403)

from datetime import date, time, datetime, timedelta
from unittest.mock import patch

import pytest

from models import db
from models.booking import Booking


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _post_booking(client, babysitter_id, booking_date="2026-09-01",
                  start_time="10:00", duration_hours=2, notes=""):
    return client.post(f"/booking/{babysitter_id}", data={
        "date": booking_date,
        "start_time": start_time,
        "duration_hours": duration_hours,
        "notes": notes,
    }, follow_redirects=True)


# ---------------------------------------------------------------------------
# POST /booking/<babysitter_id> — create a booking
# ---------------------------------------------------------------------------

def test_parent_can_create_booking(parent_client, sitter_user):
    resp = _post_booking(parent_client, sitter_user.babysitter_profile.id)
    assert resp.status_code == 200
    assert Booking.query.count() == 1
    b = Booking.query.first()
    assert b.status == "pending"
    assert b.date == date(2026, 9, 1)
    assert b.start_time == time(10, 0)
    assert b.duration_hours == 2


def test_sitter_cannot_create_booking(sitter_client, sitter_user):
    resp = _post_booking(sitter_client, sitter_user.babysitter_profile.id)
    assert Booking.query.count() == 0


def test_unauthenticated_user_cannot_create_booking(client, sitter_user):
    resp = _post_booking(client, sitter_user.babysitter_profile.id)
    # Should redirect to login
    assert Booking.query.count() == 0


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

def test_overlapping_pending_booking_is_rejected(parent_client, sitter_user):
    # First booking: 10:00–12:00
    _post_booking(parent_client, sitter_user.babysitter_profile.id,
                  booking_date="2026-09-01", start_time="10:00", duration_hours=2)
    assert Booking.query.count() == 1

    # Second booking overlaps: 11:00–13:00
    resp = _post_booking(parent_client, sitter_user.babysitter_profile.id,
                         booking_date="2026-09-01", start_time="11:00", duration_hours=2)
    assert resp.status_code == 200
    assert Booking.query.count() == 1  # second booking was rejected


def test_overlapping_accepted_booking_is_rejected(app, parent_client, parent_user, sitter_user):
    # Create an accepted booking directly
    with app.app_context():
        b = Booking(
            parent_id=parent_user.parent_profile.id,
            babysitter_id=sitter_user.babysitter_profile.id,
            date=date(2026, 9, 1),
            start_time=time(10, 0),
            duration_hours=2,
            status="accepted",
        )
        db.session.add(b)
        db.session.commit()

    # Try to create overlapping booking
    resp = _post_booking(parent_client, sitter_user.babysitter_profile.id,
                         booking_date="2026-09-01", start_time="11:00", duration_hours=2)
    assert Booking.query.count() == 1  # new booking was rejected


def test_non_overlapping_booking_is_allowed(parent_client, sitter_user):
    # First booking: 10:00–12:00
    _post_booking(parent_client, sitter_user.babysitter_profile.id,
                  booking_date="2026-09-01", start_time="10:00", duration_hours=2)
    # Second booking: 13:00–15:00 (no overlap)
    _post_booking(parent_client, sitter_user.babysitter_profile.id,
                  booking_date="2026-09-01", start_time="13:00", duration_hours=2)
    assert Booking.query.count() == 2


def test_same_time_different_date_is_allowed(parent_client, sitter_user):
    _post_booking(parent_client, sitter_user.babysitter_profile.id,
                  booking_date="2026-09-01", start_time="10:00", duration_hours=2)
    _post_booking(parent_client, sitter_user.babysitter_profile.id,
                  booking_date="2026-09-02", start_time="10:00", duration_hours=2)
    assert Booking.query.count() == 2


# ---------------------------------------------------------------------------
# POST /bookings/<id>/accept
# ---------------------------------------------------------------------------

def test_sitter_can_accept_pending_booking(sitter_client, booking):
    resp = sitter_client.post(f"/bookings/{booking.id}/accept",
                              follow_redirects=True)
    assert resp.status_code == 200
    db.session.refresh(booking)
    assert booking.status == "accepted"


def test_accepting_rejects_overlapping_pending_bookings(app, sitter_client,
                                                         parent_user, sitter_user):
    """Accepting one booking should auto-reject overlapping pending bookings."""
    with app.app_context():
        # Create a second parent user
        parent2 = __import__('models.user', fromlist=['User']).User(
            name="Parent Two", email="parent2@test.com"
        )
        parent2.set_password("Password1!")
        db.session.add(parent2)
        db.session.flush()
        from models.parent_profile import ParentProfile
        db.session.add(ParentProfile(user_id=parent2.id, children=[]))
        db.session.flush()

        b1 = Booking(
            parent_id=parent_user.parent_profile.id,
            babysitter_id=sitter_user.babysitter_profile.id,
            date=date(2026, 9, 1), start_time=time(10, 0), duration_hours=3,
            status="pending",
        )
        b2 = Booking(
            parent_id=parent2.parent_profile.id,
            babysitter_id=sitter_user.babysitter_profile.id,
            date=date(2026, 9, 1), start_time=time(11, 0), duration_hours=2,
            status="pending",
        )
        db.session.add_all([b1, b2])
        db.session.commit()
        b1_id, b2_id = b1.id, b2.id

    sitter_client.post(f"/bookings/{b1_id}/accept", follow_redirects=True)

    b1_fresh = Booking.query.get(b1_id)
    b2_fresh = Booking.query.get(b2_id)
    assert b1_fresh.status == "accepted"
    assert b2_fresh.status == "rejected"


def test_parent_cannot_accept_booking(parent_client, booking):
    resp = parent_client.post(f"/bookings/{booking.id}/accept")
    assert resp.status_code == 403


def test_cannot_accept_non_pending_booking(sitter_client, booking):
    # First accept it
    sitter_client.post(f"/bookings/{booking.id}/accept", follow_redirects=True)
    # Try to accept again
    resp = sitter_client.post(f"/bookings/{booking.id}/accept",
                               follow_redirects=True)
    assert resp.status_code == 200
    db.session.refresh(booking)
    assert booking.status == "accepted"  # still accepted, not broken


# ---------------------------------------------------------------------------
# POST /bookings/<id>/reject
# ---------------------------------------------------------------------------

def test_sitter_can_reject_pending_booking(sitter_client, booking):
    resp = sitter_client.post(f"/bookings/{booking.id}/reject",
                              follow_redirects=True)
    assert resp.status_code == 200
    db.session.refresh(booking)
    assert booking.status == "rejected"


def test_parent_cannot_reject_booking(parent_client, booking):
    resp = parent_client.post(f"/bookings/{booking.id}/reject")
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# POST /bookings/<id>/cancel
# ---------------------------------------------------------------------------

def test_parent_can_cancel_pending_booking(parent_client, booking):
    resp = parent_client.post(f"/bookings/{booking.id}/cancel",
                              follow_redirects=True)
    assert resp.status_code == 200
    db.session.refresh(booking)
    assert booking.status == "cancelled"


def test_parent_cannot_cancel_accepted_booking(parent_client, accepted_booking):
    resp = parent_client.post(f"/bookings/{accepted_booking.id}/cancel",
                              follow_redirects=True)
    assert resp.status_code == 200
    db.session.refresh(accepted_booking)
    assert accepted_booking.status == "accepted"  # unchanged


def test_sitter_cannot_cancel_booking(sitter_client, booking):
    resp = sitter_client.post(f"/bookings/{booking.id}/cancel")
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# POST /bookings/<id>/complete
# ---------------------------------------------------------------------------

def test_parent_can_complete_booking_after_start(parent_client, accepted_booking):
    """Mock datetime.now() to be after the booking start time."""
    future_now = datetime(2026, 8, 1, 12, 0)  # after 10:00 start
    with patch("routes.main.datetime") as mock_dt:
        mock_dt.now.return_value = future_now
        mock_dt.combine = datetime.combine
        resp = parent_client.post(f"/bookings/{accepted_booking.id}/complete",
                                  follow_redirects=False)
    assert resp.status_code in (200, 302)
    db.session.refresh(accepted_booking)
    assert accepted_booking.status == "completed"


def test_parent_cannot_complete_booking_before_start(parent_client, accepted_booking):
    """Mock datetime.now() to be before the booking start time."""
    early_now = datetime(2026, 8, 1, 8, 0)  # before 10:00 start
    with patch("routes.main.datetime") as mock_dt:
        mock_dt.now.return_value = early_now
        mock_dt.combine = datetime.combine
        resp = parent_client.post(f"/bookings/{accepted_booking.id}/complete",
                                  follow_redirects=False)
    assert resp.status_code in (200, 302)
    db.session.refresh(accepted_booking)
    assert accepted_booking.status == "accepted"  # unchanged


def test_sitter_cannot_complete_booking(sitter_client, accepted_booking):
    resp = sitter_client.post(f"/bookings/{accepted_booking.id}/complete")
    assert resp.status_code == 403


def test_cannot_complete_pending_booking(parent_client, booking):
    future_now = datetime(2026, 8, 1, 20, 0)
    with patch("routes.main.datetime") as mock_dt:
        mock_dt.now.return_value = future_now
        mock_dt.combine = datetime.combine
        resp = parent_client.post(f"/bookings/{booking.id}/complete",
                                  follow_redirects=True)
    assert resp.status_code == 200
    db.session.refresh(booking)
    assert booking.status == "pending"  # unchanged
