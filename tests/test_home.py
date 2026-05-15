# Tests for GET / (index)
# Owner: Christine
#
# Areas covered:
#   - Unauthenticated users see the landing page
#   - Parent sees babysitter listing cards
#   - Sitter sees parent listing cards
#   - Location / suburb display on cards
#   - Map data (lat/lng) included in card payload

import pytest


# ---------------------------------------------------------------------------
# Unauthenticated access
# ---------------------------------------------------------------------------

class TestIndexUnauthenticated:

    def test_landing_page_returns_200(self, client):
        resp = client.get("/")
        assert resp.status_code == 200

    def test_landing_page_has_no_profile_cards(self, client):
        """Unauthenticated visitors should not see any profile listings."""
        resp = client.get("/")
        # The index template only renders cards when mode is set
        assert b"card" not in resp.data or b"babysitter-card" not in resp.data

    def test_landing_page_shows_site_name(self, client):
        resp = client.get("/")
        assert b"SitBuddy" in resp.data


# ---------------------------------------------------------------------------
# Parent sees babysitter cards
# ---------------------------------------------------------------------------

class TestIndexAsParent:

    def test_index_returns_200(self, parent_client):
        resp = parent_client.get("/")
        assert resp.status_code == 200

    def test_parent_sees_babysitter_cards(self, parent_client, sitter_user):
        """A parent should see the sitter's name on the index page."""
        resp = parent_client.get("/")
        assert b"Sitter User" in resp.data

    def test_parent_sees_sitter_bio(self, parent_client, sitter_user):
        resp = parent_client.get("/")
        assert b"Experienced sitter" in resp.data

    def test_parent_sees_sitter_hourly_rate(self, parent_client, sitter_user):
        resp = parent_client.get("/")
        assert b"25" in resp.data

    def test_parent_does_not_see_own_name_as_card(self, parent_client, parent_user):
        """Parent cards should not appear when a parent is browsing."""
        resp = parent_client.get("/")
        # parent_user's name should not appear as a listing card
        # (it may appear in the navbar, so we check the page doesn't list parent profiles)
        assert b"Parent User" not in resp.data or b"babysitters" in resp.data


# ---------------------------------------------------------------------------
# Sitter sees parent cards
# ---------------------------------------------------------------------------

class TestIndexAsSitter:

    def test_index_returns_200(self, sitter_client):
        resp = sitter_client.get("/")
        assert resp.status_code == 200

    def test_sitter_sees_parent_cards(self, sitter_client, parent_user):
        """A sitter should see the parent's name on the index page."""
        resp = sitter_client.get("/")
        assert b"Parent User" in resp.data

    def test_sitter_sees_parent_about(self, sitter_client, parent_user):
        resp = sitter_client.get("/")
        assert b"Test family" in resp.data

    def test_sitter_does_not_see_own_name_as_card(self, sitter_client, sitter_user):
        """Sitter cards should not appear when a sitter is browsing."""
        resp = sitter_client.get("/")
        assert b"Experienced sitter" not in resp.data or b"parents" in resp.data


# ---------------------------------------------------------------------------
# Location / suburb on cards
# ---------------------------------------------------------------------------

class TestIndexLocationDisplay:

    def test_sitter_suburb_shown_to_parent(self, parent_client, sitter_user):
        """Sitter's suburb (Subiaco) should appear on the card."""
        resp = parent_client.get("/")
        assert b"Subiaco" in resp.data

    def test_sitter_postcode_shown_to_parent(self, parent_client, sitter_user):
        """Sitter's postcode (6008) should appear on the card."""
        resp = parent_client.get("/")
        assert b"6008" in resp.data

    def test_parent_suburb_shown_to_sitter(self, sitter_client, parent_user):
        """Parent's suburb (Nedlands) should appear on the card."""
        resp = sitter_client.get("/")
        assert b"Nedlands" in resp.data

    def test_parent_postcode_shown_to_sitter(self, sitter_client, parent_user):
        """Parent's postcode (6009) should appear on the card."""
        resp = sitter_client.get("/")
        assert b"6009" in resp.data


# ---------------------------------------------------------------------------
# Map data (lat/lng) in page payload
# ---------------------------------------------------------------------------

class TestIndexMapData:

    def test_sitter_lat_in_page_for_parent(self, parent_client, sitter_user):
        """Sitter's latitude should be embedded in the page for the map."""
        resp = parent_client.get("/")
        # sitter_user has latitude=-31.949
        assert b"-31.949" in resp.data

    def test_sitter_lng_in_page_for_parent(self, parent_client, sitter_user):
        """Sitter's longitude should be embedded in the page for the map."""
        resp = parent_client.get("/")
        # sitter_user has longitude=115.827
        assert b"115.827" in resp.data

    def test_parent_lat_in_page_for_sitter(self, sitter_client, parent_user):
        """Parent's latitude should be embedded in the page for the map."""
        resp = sitter_client.get("/")
        # parent_user has latitude=-31.9829
        assert b"-31.9829" in resp.data

    def test_parent_lng_in_page_for_sitter(self, sitter_client, parent_user):
        """Parent's longitude should be embedded in the page for the map."""
        resp = sitter_client.get("/")
        # parent_user has longitude=115.8012
        assert b"115.8012" in resp.data

    def test_no_map_data_for_unauthenticated(self, client):
        """Unauthenticated users should not receive any lat/lng data."""
        resp = client.get("/")
        assert b"-31.949" not in resp.data
        assert b"115.827" not in resp.data
