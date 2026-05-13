import json
import pytest
from unittest.mock import patch, MagicMock
from models.user import User


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _urlopen_mock(items):
    """Context-manager mock for urllib.request.urlopen returning items as JSON."""
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps(items).encode()
    mock_resp.__enter__ = MagicMock(return_value=mock_resp)
    mock_resp.__exit__ = MagicMock(return_value=False)
    return mock_resp


_NEDLANDS = {
    "lat": "-31.9829",
    "lon": "115.8012",
    "address": {
        "suburb": "Nedlands",
        "postcode": "6009",
        "state": "Western Australia",
        "country": "Australia",
        "country_code": "au",
    },
}

_BONDI = {
    "lat": "-33.8915",
    "lon": "151.2767",
    "address": {
        "suburb": "Bondi",
        "postcode": "2026",
        "state": "New South Wales",
        "country": "Australia",
        "country_code": "au",
    },
}


# ---------------------------------------------------------------------------
# /auth/postcode-search — query routing
# ---------------------------------------------------------------------------

def test_query_too_short_returns_empty(client):
    resp = client.get("/auth/postcode-search?q=n")
    assert resp.get_json() == []


def test_empty_query_returns_empty(client):
    resp = client.get("/auth/postcode-search")
    assert resp.get_json() == []


def test_four_digit_query_uses_postalcode_param(client):
    with patch("urllib.request.Request") as mock_req, \
         patch("urllib.request.urlopen", return_value=_urlopen_mock([])):
        client.get("/auth/postcode-search?q=6009")

    url = mock_req.call_args[0][0]
    assert "postalcode=6009" in url
    assert "city=" not in url


def test_suburb_name_uses_city_param(client):
    with patch("urllib.request.Request") as mock_req, \
         patch("urllib.request.urlopen", return_value=_urlopen_mock([])):
        client.get("/auth/postcode-search?q=nedl")

    url = mock_req.call_args[0][0]
    assert "city=nedl" in url
    assert "postalcode=" not in url


def test_partial_digit_query_uses_city_param(client):
    # "600" is digits but fewer than 4, must NOT use postalcode=
    with patch("urllib.request.Request") as mock_req, \
         patch("urllib.request.urlopen", return_value=_urlopen_mock([])):
        client.get("/auth/postcode-search?q=600")

    url = mock_req.call_args[0][0]
    assert "city=" in url
    assert "postalcode=" not in url


def test_request_includes_user_agent_header(client):
    with patch("urllib.request.Request") as mock_req, \
         patch("urllib.request.urlopen", return_value=_urlopen_mock([])):
        client.get("/auth/postcode-search?q=6009")

    headers = mock_req.call_args[1].get("headers", {})
    assert headers.get("User-Agent") == "SitBuddy/1.0"


# ---------------------------------------------------------------------------
# /auth/postcode-search — response shape and filtering
# ---------------------------------------------------------------------------

def test_result_contains_all_required_fields(client):
    with patch("urllib.request.urlopen", return_value=_urlopen_mock([_NEDLANDS])):
        resp = client.get("/auth/postcode-search?q=6009")

    data = resp.get_json()
    assert len(data) == 1
    r = data[0]
    assert r["suburb"] == "Nedlands"
    assert r["postcode"] == "6009"
    assert r["state"] == "Western Australia"
    assert r["lat"] == pytest.approx(-31.9829)
    assert r["lon"] == pytest.approx(115.8012)


def test_result_without_postcode_is_skipped(client):
    no_postcode = {
        "lat": "-31.9829", "lon": "115.8012",
        "address": {"suburb": "Nedlands", "state": "Western Australia"},
    }
    with patch("urllib.request.urlopen", return_value=_urlopen_mock([no_postcode])):
        resp = client.get("/auth/postcode-search?q=6009")

    assert resp.get_json() == []


def test_result_without_suburb_is_skipped(client):
    no_suburb = {
        "lat": "-31.9829", "lon": "115.8012",
        "address": {"postcode": "6009", "state": "Western Australia"},
    }
    with patch("urllib.request.urlopen", return_value=_urlopen_mock([no_suburb])):
        resp = client.get("/auth/postcode-search?q=6009")

    assert resp.get_json() == []


def test_suburb_falls_back_to_town_field(client):
    town_result = {
        "lat": "-31.9", "lon": "115.8",
        "address": {"town": "Rockingham", "postcode": "6168", "state": "Western Australia"},
    }
    with patch("urllib.request.urlopen", return_value=_urlopen_mock([town_result])):
        resp = client.get("/auth/postcode-search?q=rock")

    data = resp.get_json()
    assert len(data) == 1
    assert data[0]["suburb"] == "Rockingham"


def test_duplicate_suburb_postcode_deduplicated(client):
    with patch("urllib.request.urlopen", return_value=_urlopen_mock([_NEDLANDS, _NEDLANDS])):
        resp = client.get("/auth/postcode-search?q=nedlands")

    assert len(resp.get_json()) == 1


def test_results_capped_at_eight(client):
    many = [
        {
            "lat": f"-31.{i}", "lon": "115.8",
            "address": {
                "suburb": f"Suburb{i}",
                "postcode": f"60{i:02d}",
                "state": "Western Australia",
            },
        }
        for i in range(20)
    ]
    with patch("urllib.request.urlopen", return_value=_urlopen_mock(many)):
        resp = client.get("/auth/postcode-search?q=suburb")

    assert len(resp.get_json()) == 8


def test_nominatim_error_returns_empty_gracefully(client):
    with patch("urllib.request.urlopen", side_effect=Exception("timeout")):
        resp = client.get("/auth/postcode-search?q=nedlands")

    assert resp.status_code == 200
    assert resp.get_json() == []


def test_non_wa_result_is_included(client):
    # Non-WA postcodes are allowed; the WA warning is frontend-only
    with patch("urllib.request.urlopen", return_value=_urlopen_mock([_BONDI])):
        resp = client.get("/auth/postcode-search?q=bondi")

    data = resp.get_json()
    assert len(data) == 1
    assert data[0]["state"] == "New South Wales"


# ---------------------------------------------------------------------------
# Setup profile — lat/lon form submission
# ---------------------------------------------------------------------------

def test_setup_profile_saves_lat_lon_from_form(auth_client):
    with auth_client.session_transaction() as sess:
        sess["pending_role"] = "parent"

    auth_client.post("/auth/setup-profile/details", data={
        "suburb": "Nedlands",
        "postcode": "6009",
        "lat": "-31.9829",
        "lon": "115.8012",
        "children_json": "[]",
    })

    user = User.query.filter_by(email="test@test.com").first()
    assert user.suburb == "Nedlands"
    assert user.postcode == "6009"
    assert user.latitude == pytest.approx(-31.9829)
    assert user.longitude == pytest.approx(115.8012)


def test_setup_profile_rejects_invalid_postcode_format(auth_client):
    with auth_client.session_transaction() as sess:
        sess["pending_role"] = "parent"

    auth_client.post("/auth/setup-profile/details", data={
        "suburb": "Somewhere",
        "postcode": "ABCD",
        "lat": "-31.9",
        "lon": "115.8",
        "children_json": "[]",
    })

    # Flash message is stored in session (setup page doesn't consume it)
    with auth_client.session_transaction() as sess:
        flashes = sess.get("_flashes", [])
    assert any("valid 4-digit postcode" in msg for _, msg in flashes)


def test_setup_profile_missing_coords_stores_null(auth_client):
    with auth_client.session_transaction() as sess:
        sess["pending_role"] = "parent"

    auth_client.post("/auth/setup-profile/details", data={
        "suburb": "Nedlands",
        "postcode": "6009",
        "children_json": "[]",
        # lat and lon intentionally omitted
    })

    user = User.query.filter_by(email="test@test.com").first()
    assert user.latitude is None
    assert user.longitude is None
