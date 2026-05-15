# Tests for booking ratings
# Owner: bookings team member (or profiles team member)
#
# Areas to cover:
#   - POST /bookings/<id>/rate: submit a rating for a completed booking
#   - Cannot rate a booking that is not completed
#   - Cannot rate the same booking twice
#   - Rating score must be 1–5
#   - Average rating on profile updates after submission

import pytest

from models import db
from models.rating import Rating


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _post_rating(client, booking_id, score, comment=""):
    return client.post(f"/bookings/{booking_id}/rate", data={
        "score": score,
        "comment": comment,
    }, follow_redirects=True)


# ---------------------------------------------------------------------------
# POST /bookings/<id>/rate — successful submission
# ---------------------------------------------------------------------------

def test_parent_can_rate_completed_booking(parent_client, completed_booking, sitter_user):
    resp = _post_rating(parent_client, completed_booking.id, score=5,
                        comment="Great babysitter!")
    assert resp.status_code == 200
    assert Rating.query.count() == 1
    r = Rating.query.first()
    assert r.score == 5
    assert r.comment == "Great babysitter!"
    assert r.ratee_id == sitter_user.id


def test_sitter_can_rate_completed_booking(sitter_client, completed_booking, parent_user):
    resp = _post_rating(sitter_client, completed_booking.id, score=4,
                        comment="Nice family.")
    assert resp.status_code == 200
    assert Rating.query.count() == 1
    r = Rating.query.first()
    assert r.score == 4
    assert r.ratee_id == parent_user.id


def test_rating_without_comment_is_valid(parent_client, completed_booking):
    resp = _post_rating(parent_client, completed_booking.id, score=3, comment="")
    assert resp.status_code == 200
    assert Rating.query.count() == 1
    assert Rating.query.first().comment is None


def test_both_parties_can_rate_same_booking(app, parent_client, sitter_client,
                                             parent_user, sitter_user,
                                             completed_booking):
    """Both parent and sitter can each rate the same completed booking."""
    # Parent rates sitter
    _post_rating(parent_client, completed_booking.id, score=5)
    assert Rating.query.count() == 1

    # Sitter rates parent — add directly to DB since sitter_client shares session
    with app.app_context():
        r2 = Rating(
            booking_id=completed_booking.id,
            rater_id=sitter_user.id,
            ratee_id=parent_user.id,
            score=4,
        )
        db.session.add(r2)
        db.session.commit()

    assert Rating.query.count() == 2


# ---------------------------------------------------------------------------
# Cannot rate non-completed bookings
# ---------------------------------------------------------------------------

def test_cannot_rate_pending_booking(parent_client, booking):
    resp = _post_rating(parent_client, booking.id, score=5)
    assert resp.status_code == 200
    assert Rating.query.count() == 0


def test_cannot_rate_accepted_booking(parent_client, accepted_booking):
    resp = _post_rating(parent_client, accepted_booking.id, score=5)
    assert resp.status_code == 200
    assert Rating.query.count() == 0


def test_cannot_rate_rejected_booking(app, parent_client, parent_user, sitter_user):
    from models.booking import Booking
    from datetime import date, time
    with app.app_context():
        b = Booking(
            parent_id=parent_user.parent_profile.id,
            babysitter_id=sitter_user.babysitter_profile.id,
            date=date(2026, 1, 1),
            start_time=time(10, 0),
            duration_hours=2,
            status="rejected",
        )
        db.session.add(b)
        db.session.commit()
        bid = b.id

    resp = _post_rating(parent_client, bid, score=5)
    assert Rating.query.count() == 0


# ---------------------------------------------------------------------------
# Cannot rate the same booking twice
# ---------------------------------------------------------------------------

def test_cannot_rate_same_booking_twice(parent_client, completed_booking):
    _post_rating(parent_client, completed_booking.id, score=5)
    resp = _post_rating(parent_client, completed_booking.id, score=3)
    assert resp.status_code == 200
    # Still only one rating
    assert Rating.query.count() == 1
    assert Rating.query.first().score == 5  # original score unchanged


# ---------------------------------------------------------------------------
# Score validation (1–5)
# ---------------------------------------------------------------------------

def test_score_of_1_is_valid(parent_client, completed_booking):
    resp = _post_rating(parent_client, completed_booking.id, score=1)
    assert resp.status_code == 200
    assert Rating.query.count() == 1


def test_score_of_5_is_valid(parent_client, completed_booking):
    resp = _post_rating(parent_client, completed_booking.id, score=5)
    assert resp.status_code == 200
    assert Rating.query.count() == 1


def test_score_of_0_is_invalid(parent_client, completed_booking):
    resp = _post_rating(parent_client, completed_booking.id, score=0)
    assert resp.status_code == 200
    assert Rating.query.count() == 0


def test_score_of_6_is_invalid(parent_client, completed_booking):
    resp = _post_rating(parent_client, completed_booking.id, score=6)
    assert resp.status_code == 200
    assert Rating.query.count() == 0


def test_negative_score_is_invalid(parent_client, completed_booking):
    resp = _post_rating(parent_client, completed_booking.id, score=-1)
    assert resp.status_code == 200
    assert Rating.query.count() == 0


# ---------------------------------------------------------------------------
# Average rating updates after submission
# ---------------------------------------------------------------------------

def test_average_rating_updates_after_single_rating(app, parent_client,
                                                      completed_booking, sitter_user):
    _post_rating(parent_client, completed_booking.id, score=4)
    with app.app_context():
        from models.babysitter_profile import BabysitterProfile
        profile = BabysitterProfile.query.filter_by(user_id=sitter_user.id).first()
        assert profile.get_average_rating() == 4.0
        assert profile.get_rating_count() == 1


def test_average_rating_is_correct_with_multiple_ratings(app, parent_client,
                                                           parent_user, sitter_user,
                                                           completed_booking):
    """Parent rates sitter 4 stars; sitter rates parent 2 stars directly."""
    # Parent rates sitter via HTTP
    _post_rating(parent_client, completed_booking.id, score=4)

    # Sitter rates parent directly via DB
    with app.app_context():
        r2 = Rating(
            booking_id=completed_booking.id,
            rater_id=sitter_user.id,
            ratee_id=parent_user.id,
            score=2,
        )
        db.session.add(r2)
        db.session.commit()

        from models.babysitter_profile import BabysitterProfile
        from models.parent_profile import ParentProfile

        sitter_profile = BabysitterProfile.query.filter_by(user_id=sitter_user.id).first()
        parent_profile_obj = ParentProfile.query.filter_by(user_id=parent_user.id).first()

        assert sitter_profile.get_average_rating() == 4.0
        assert sitter_profile.get_rating_count() == 1
        assert parent_profile_obj.get_average_rating() == 2.0
        assert parent_profile_obj.get_rating_count() == 1


def test_average_rating_is_none_when_no_ratings(app, sitter_user):
    with app.app_context():
        from models.babysitter_profile import BabysitterProfile
        profile = BabysitterProfile.query.filter_by(user_id=sitter_user.id).first()
        assert profile.get_average_rating() is None
        assert profile.get_rating_count() == 0


def test_average_rating_rounds_to_one_decimal(app, parent_client, sitter_user,
                                               parent_user, completed_booking):
    """Two ratings of 4 and 5 should average to 4.5."""
    _post_rating(parent_client, completed_booking.id, score=4)

    # Add a second rating directly via DB
    with app.app_context():
        r2 = Rating(
            booking_id=completed_booking.id,
            rater_id=parent_user.id,
            ratee_id=sitter_user.id,
            score=5,
        )
        # Use a different rater to avoid unique constraint
        from models.user import User
        extra = User(name="Extra", email="extra@test.com")
        extra.set_password("Password1!")
        db.session.add(extra)
        db.session.flush()
        r2.rater_id = extra.id
        db.session.add(r2)
        db.session.commit()

        from models.babysitter_profile import BabysitterProfile
        profile = BabysitterProfile.query.filter_by(user_id=sitter_user.id).first()
        assert profile.get_average_rating() == 4.5
