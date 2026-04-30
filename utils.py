import json
import urllib.request
from urllib.parse import quote as urlquote

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# Approximate suburb centroids for known Perth postcodes (lat, lng)
POSTCODE_COORDS = {
    "6003": (-31.9437, 115.8596),
    "6007": (-31.9277, 115.8476),
    "6008": (-31.9490, 115.8270),
    "6009": (-31.9829, 115.8012),
    "6010": (-31.9826, 115.7795),
    "6011": (-31.9966, 115.7522),
    "6014": (-31.9391, 115.7869),
    "6050": (-31.9247, 115.8736),
    "6102": (-31.9769, 115.8913),
    "6160": (-32.0569, 115.7439),
}


def geocode_suburb(suburb, postcode):
    """Return (lat, lng) for a suburb/postcode, or (None, None) on failure."""
    if postcode and postcode in POSTCODE_COORDS:
        return POSTCODE_COORDS[postcode]
    q = f"{suburb}, {postcode}, Australia" if suburb else f"{postcode}, Australia"
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={urlquote(q)}&format=json&limit=1"
        req = urllib.request.Request(url, headers={"User-Agent": "SitBuddy/1.0"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read())
            if data:
                return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception:
        pass
    return None, None


POSTCODE_SUBURB = {
    "6003": "Highgate",
    "6007": "Leederville",
    "6008": "Subiaco",
    "6009": "Nedlands",
    "6010": "Claremont",
    "6011": "Cottesloe",
    "6019": "Scarborough",
    "6050": "Mount Lawley",
    "6100": "Victoria Park",
    "6160": "Fremantle",
}
