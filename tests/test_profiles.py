# Tests for profile viewing and editing
# Owner: xin
#
# Areas covered:
#   - GET /babysitter/<id>: view sitter profile (bio, rate, availability)
#   - POST /babysitter/<id>/edit: update bio, rate, availability, suburb/postcode
#   - GET /parent/<id>: view parent profile (children, about, location)
#   - POST /parent/<id>/edit: update children, about, suburb/postcode
#   - Non-owners cannot edit another user's profile (403)
#   - Unauthenticated users are redirected to login
#   - Suburb/postcode saved correctly on edit

import json
import pytest

from models import db as _db
from models.user import User
from models.babysitter_profile import BabysitterProfile
from models.parent_profile import ParentProfile


# ---------------------------------------------------------------------------
# Additional fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def second_parent_user(app):
    """A second parent user (used to test 403 on edit)."""
    user = User(
        name="Other Parent",
        email="other_parent@test.com",
        suburb="Subiaco",
        postcode="6008",
    )
    user.set_password("Password1!")
    _db.session.add(user)
    _db.session.flush()
    _db.session.add(ParentProfile(user_id=user.id, children=[], about="Other family"))
    _db.session.commit()
    return user


@pytest.fixture
def second_sitter_user(app):
    """A second sitter user (used to test 403 on edit)."""
    user = User(
        name="Other Sitter",
        email="other_sitter@test.com",
        suburb="Fremantle",
        postcode="6160",
    )
    user.set_password("Password1!")
    _db.session.add(user)
    _db.session.flush()
    _db.session.add(BabysitterProfile(
        user_id=user.id,
        bio="Other sitter bio",
        hourly_rate=20.0,
        experience_years=1,
    ))
    _db.session.commit()
    return user


# ---------------------------------------------------------------------------
# GET /babysitter/<id> — view sitter profile
# ---------------------------------------------------------------------------

class TestViewBabysitterProfile:

    def test_sitter_can_view_own_profile(self, sitter_client, sitter_user):
        pid = sitter_user.babysitter_profile.id
        resp = sitter_client.get(f"/babysitter/{pid}")
        assert resp.status_code == 200

    def test_parent_can_view_sitter_profile(self, parent_client, sitter_user):
        pid = sitter_user.babysitter_profile.id
        resp = parent_client.get(f"/babysitter/{pid}")
        assert resp.status_code == 200

    def test_profile_shows_bio(self, parent_client, sitter_user):
        pid = sitter_user.babysitter_profile.id
        resp = parent_client.get(f"/babysitter/{pid}")
        assert b"Experienced sitter" in resp.data

    def test_profile_shows_hourly_rate(self, parent_client, sitter_user):
        pid = sitter_user.babysitter_profile.id
        resp = parent_client.get(f"/babysitter/{pid}")
        assert b"25" in resp.data

    def test_profile_shows_sitter_name(self, parent_client, sitter_user):
        pid = sitter_user.babysitter_profile.id
        resp = parent_client.get(f"/babysitter/{pid}")
        assert b"Sitter User" in resp.data

    def test_unauthenticated_redirected_to_login(self, client, sitter_user):
        pid = sitter_user.babysitter_profile.id
        resp = client.get(f"/babysitter/{pid}")
        assert resp.status_code == 302
        assert "/auth/login" in resp.headers["Location"]

    def test_nonexistent_profile_returns_404(self, parent_client):
        resp = parent_client.get("/babysitter/99999")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# POST /babysitter/<id>/edit — edit sitter profile
# ---------------------------------------------------------------------------

class TestEditBabysitterProfile:

    def test_sitter_can_update_bio(self, sitter_client, sitter_user):
        pid = sitter_user.babysitter_profile.id
        sitter_client.post(f"/babysitter/{pid}/edit", data={
            "bio": "Updated bio text",
            "hourly_rate": "25.0",
            "experience_years": "3",
            "suburb": "Subiaco",
            "postcode": "6008",
        })
        profile = BabysitterProfile.query.get(pid)
        assert profile.bio == "Updated bio text"

    def test_sitter_can_update_hourly_rate(self, sitter_client, sitter_user):
        pid = sitter_user.babysitter_profile.id
        sitter_client.post(f"/babysitter/{pid}/edit", data={
            "bio": "Bio",
            "hourly_rate": "30.0",
            "experience_years": "3",
            "suburb": "Subiaco",
            "postcode": "6008",
        })
        profile = BabysitterProfile.query.get(pid)
        assert profile.hourly_rate == pytest.approx(30.0)

    def test_sitter_can_update_experience_years(self, sitter_client, sitter_user):
        pid = sitter_user.babysitter_profile.id
        sitter_client.post(f"/babysitter/{pid}/edit", data={
            "bio": "Bio",
            "hourly_rate": "25.0",
            "experience_years": "5",
            "suburb": "Subiaco",
            "postcode": "6008",
        })
        profile = BabysitterProfile.query.get(pid)
        assert profile.experience_years == 5

    def test_sitter_can_update_availability(self, sitter_client, sitter_user):
        pid = sitter_user.babysitter_profile.id
        sitter_client.post(f"/babysitter/{pid}/edit", data={
            "bio": "Bio",
            "hourly_rate": "25.0",
            "experience_years": "3",
            "availability": ["Mon", "Wed", "Fri"],
            "suburb": "Subiaco",
            "postcode": "6008",
        })
        profile = BabysitterProfile.query.get(pid)
        days = json.loads(profile.availability)
        assert days == ["Mon", "Wed", "Fri"]

    def test_sitter_can_update_suburb_and_postcode(self, sitter_client, sitter_user):
        pid = sitter_user.babysitter_profile.id
        sitter_client.post(f"/babysitter/{pid}/edit", data={
            "bio": "Bio",
            "hourly_rate": "25.0",
            "experience_years": "3",
            "suburb": "Nedlands",
            "postcode": "6009",
        })
        user = User.query.get(sitter_user.id)
        assert user.suburb == "Nedlands"
        assert user.postcode == "6009"

    def test_edit_redirects_to_profile_page(self, sitter_client, sitter_user):
        pid = sitter_user.babysitter_profile.id
        resp = sitter_client.post(f"/babysitter/{pid}/edit", data={
            "bio": "Bio",
            "hourly_rate": "25.0",
            "experience_years": "3",
            "suburb": "Subiaco",
            "postcode": "6008",
        })
        assert resp.status_code == 302
        assert f"/babysitter/{pid}" in resp.headers["Location"]

    def test_parent_cannot_edit_sitter_profile(self, parent_client, sitter_user):
        pid = sitter_user.babysitter_profile.id
        resp = parent_client.post(f"/babysitter/{pid}/edit", data={
            "bio": "Hacked bio",
            "hourly_rate": "1.0",
            "experience_years": "0",
            "suburb": "Subiaco",
            "postcode": "6008",
        })
        assert resp.status_code == 403

    def test_sitter_cannot_edit_another_sitters_profile(
        self, sitter_client, second_sitter_user
    ):
        pid = second_sitter_user.babysitter_profile.id
        resp = sitter_client.post(f"/babysitter/{pid}/edit", data={
            "bio": "Hacked",
            "hourly_rate": "1.0",
            "experience_years": "0",
            "suburb": "Fremantle",
            "postcode": "6160",
        })
        assert resp.status_code == 403

    def test_invalid_hourly_rate_rejected(self, sitter_client, sitter_user):
        pid = sitter_user.babysitter_profile.id
        sitter_client.post(f"/babysitter/{pid}/edit", data={
            "bio": "Bio",
            "hourly_rate": "999.0",  # exceeds max 200
            "experience_years": "3",
            "suburb": "Subiaco",
            "postcode": "6008",
        })
        profile = BabysitterProfile.query.get(pid)
        assert profile.hourly_rate == pytest.approx(25.0)  # unchanged

    def test_invalid_experience_years_rejected(self, sitter_client, sitter_user):
        pid = sitter_user.babysitter_profile.id
        sitter_client.post(f"/babysitter/{pid}/edit", data={
            "bio": "Bio",
            "hourly_rate": "25.0",
            "experience_years": "100",  # exceeds max 50
            "suburb": "Subiaco",
            "postcode": "6008",
        })
        profile = BabysitterProfile.query.get(pid)
        assert profile.experience_years == 3  # unchanged

    def test_unauthenticated_edit_redirected(self, client, sitter_user):
        pid = sitter_user.babysitter_profile.id
        resp = client.post(f"/babysitter/{pid}/edit", data={
            "bio": "Hacked",
            "hourly_rate": "25.0",
            "experience_years": "3",
        })
        assert resp.status_code == 302
        assert "/auth/login" in resp.headers["Location"]


# ---------------------------------------------------------------------------
# GET /parent/<id> — view parent profile
# ---------------------------------------------------------------------------

class TestViewParentProfile:

    def test_parent_can_view_own_profile(self, parent_client, parent_user):
        pid = parent_user.parent_profile.id
        resp = parent_client.get(f"/parent/{pid}")
        assert resp.status_code == 200

    def test_sitter_can_view_parent_profile(self, sitter_client, parent_user):
        pid = parent_user.parent_profile.id
        resp = sitter_client.get(f"/parent/{pid}")
        assert resp.status_code == 200

    def test_profile_shows_parent_name(self, sitter_client, parent_user):
        pid = parent_user.parent_profile.id
        resp = sitter_client.get(f"/parent/{pid}")
        assert b"Parent User" in resp.data

    def test_profile_shows_about(self, sitter_client, parent_user):
        pid = parent_user.parent_profile.id
        resp = sitter_client.get(f"/parent/{pid}")
        assert b"Test family" in resp.data

    def test_unauthenticated_redirected_to_login(self, client, parent_user):
        pid = parent_user.parent_profile.id
        resp = client.get(f"/parent/{pid}")
        assert resp.status_code == 302
        assert "/auth/login" in resp.headers["Location"]

    def test_nonexistent_profile_returns_404(self, sitter_client):
        resp = sitter_client.get("/parent/99999")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# POST /parent/<id>/edit — edit parent profile
# ---------------------------------------------------------------------------

class TestEditParentProfile:

    def test_parent_can_update_about(self, parent_client, parent_user):
        pid = parent_user.parent_profile.id
        parent_client.post(f"/parent/{pid}/edit", data={
            "about": "Updated family notes",
            "children_json": "[]",
            "suburb": "Nedlands",
            "postcode": "6009",
        })
        profile = ParentProfile.query.get(pid)
        assert profile.about == "Updated family notes"

    def test_parent_can_update_children(self, parent_client, parent_user):
        pid = parent_user.parent_profile.id
        children = json.dumps([{"name": "Alice", "age": 5}, {"name": "Bob", "age": 3}])
        parent_client.post(f"/parent/{pid}/edit", data={
            "about": "Notes",
            "children_json": children,
            "suburb": "Nedlands",
            "postcode": "6009",
        })
        profile = ParentProfile.query.get(pid)
        assert len(profile.children) == 2
        assert profile.children[0]["name"] == "Alice"
        assert profile.children[1]["age"] == 3

    def test_parent_can_update_suburb_and_postcode(self, parent_client, parent_user):
        pid = parent_user.parent_profile.id
        parent_client.post(f"/parent/{pid}/edit", data={
            "about": "Notes",
            "children_json": "[]",
            "suburb": "Subiaco",
            "postcode": "6008",
        })
        user = User.query.get(parent_user.id)
        assert user.suburb == "Subiaco"
        assert user.postcode == "6008"

    def test_edit_redirects_to_profile_page(self, parent_client, parent_user):
        pid = parent_user.parent_profile.id
        resp = parent_client.post(f"/parent/{pid}/edit", data={
            "about": "Notes",
            "children_json": "[]",
            "suburb": "Nedlands",
            "postcode": "6009",
        })
        assert resp.status_code == 302
        assert f"/parent/{pid}" in resp.headers["Location"]

    def test_sitter_cannot_edit_parent_profile(self, sitter_client, parent_user):
        pid = parent_user.parent_profile.id
        resp = sitter_client.post(f"/parent/{pid}/edit", data={
            "about": "Hacked",
            "children_json": "[]",
            "suburb": "Nedlands",
            "postcode": "6009",
        })
        assert resp.status_code == 403

    def test_parent_cannot_edit_another_parents_profile(
        self, parent_client, second_parent_user
    ):
        pid = second_parent_user.parent_profile.id
        resp = parent_client.post(f"/parent/{pid}/edit", data={
            "about": "Hacked",
            "children_json": "[]",
            "suburb": "Subiaco",
            "postcode": "6008",
        })
        assert resp.status_code == 403

    def test_invalid_postcode_rejected(self, parent_client, parent_user):
        pid = parent_user.parent_profile.id
        parent_client.post(f"/parent/{pid}/edit", data={
            "about": "Notes",
            "children_json": "[]",
            "suburb": "Nowhere",
            "postcode": "9999",  # not in POSTCODE_SUBURB
        })
        user = User.query.get(parent_user.id)
        assert user.postcode == "6009"  # unchanged

    def test_unauthenticated_edit_redirected(self, client, parent_user):
        pid = parent_user.parent_profile.id
        resp = client.post(f"/parent/{pid}/edit", data={
            "about": "Hacked",
            "children_json": "[]",
        })
        assert resp.status_code == 302
        assert "/auth/login" in resp.headers["Location"]

    def test_children_json_invalid_falls_back_to_empty(self, parent_client, parent_user):
        pid = parent_user.parent_profile.id
        parent_client.post(f"/parent/{pid}/edit", data={
            "about": "Notes",
            "children_json": "not-valid-json",
            "suburb": "Nedlands",
            "postcode": "6009",
        })
        profile = ParentProfile.query.get(pid)
        assert profile.children == []
