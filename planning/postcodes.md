# Location handling spec

## Overview

Location is stored at the **user level** and is used for two purposes:
1. Displaying suburb on parent and sitter profiles
2. Distance-based filtering on the map search page

We use **Nominatim (OpenStreetMap)** for postcode lookup and coordinate resolution.

---

## What to store

When a user enters their postcode, resolve and store the following on the `User` model:

```python
postcode    = db.Column(db.String(10))
suburb      = db.Column(db.String(100))
latitude    = db.Column(db.Float)
longitude   = db.Column(db.Float)
```

Never store just the postcode alone. The coordinates are required for distance filtering on the map and should be captured at the same time as the postcode, not resolved later.

---

## Nominatim lookup

**Endpoint:**
```
GET https://nominatim.openstreetmap.org/search
  ?postalcode={postcode}
  &country=AU
  &format=json
  &limit=1
  &addressdetails=1
```

**Example response fields to extract:**
```json
{
  "lat": "-31.9505",
  "lon": "115.8605",
  "address": {
    "postcode": "6000",
    "suburb": "Perth",
    "state": "Western Australia"
  }
}
```

Extract and store: `lat`, `lon`, `address.suburb` (fall back to `address.town` or `address.city` if suburb is absent), and `address.state`.

**Important:** Nominatim's usage policy requires a descriptive `User-Agent` header and asks that requests are not made more than 1 per second. Always include:
```
User-Agent: SitBuddy/1.0
```

---

## Frontend behaviour

### Postcode input field

- Accepts 4-digit numeric input only (Australian postcodes)
- **Debounce** the Nominatim lookup — wait **300ms** after the user stops typing before firing the request
- Show a loading spinner or subtle indicator while the request is in flight

### On successful lookup

- Display the resolved suburb and state below the field as a confirmation:
  ```
  ✓ Ellenbrook, Western Australia
  ```
- Store lat/lon in hidden fields (or component state) ready for form submission
- Enable the Continue / Save button

### On failed lookup (no results returned)

- Show an inline error below the field:
  ```
  We couldn't find that postcode. Please check and try again.
  ```
- Disable the Continue / Save button until a valid postcode is entered

### Perth soft warning

If the lookup succeeds but `address.state` is **not** `"Western Australia"`, show a non-blocking warning rather than an error:

```
⚠ This service is currently focused on the Perth area.
  Availability may be limited in your location.
```

Still allow the user to proceed. Do not block non-WA postcodes — the API has them and blocking would be misleading.

---

## Server-side validation

Even though the frontend validates via Nominatim, the backend should do a lightweight sanity check on submission:

```python
import re

def is_valid_postcode_format(postcode: str) -> bool:
    return bool(re.match(r'^\d{4}$', postcode))
```

On the signup and profile edit routes, reject submissions where `postcode` doesn't match the 4-digit pattern. This catches any attempt to bypass the frontend.

Optionally, the backend can re-query Nominatim on submission to verify the postcode and re-resolve coordinates, but for a class project trusting the frontend-resolved values with a format check is sufficient.

---

## Signup flow

Location fields appear on **Step 2 (setup profile)**, alongside profile details.

The suburb and state are shown as read-only confirmation text, not editable fields. The user only types their postcode.

---

## Profile editing

When a user edits their account/profile settings later, the postcode field should behave identically to signup:

- Pre-populate with their stored postcode on load
- Re-run the Nominatim lookup and update lat/lon/suburb if they change it
- On save, write the updated postcode, suburb, latitude, and longitude to the user record

Do not allow saving the profile with a postcode that failed lookup — the coordinates would be stale or missing, which breaks the map filtering.

---

## Map and distance filtering

The stored `latitude` and `longitude` on each user are used for the distance filter on the search/map page.

**Distance calculation (backend):**

Use the **Haversine formula** to calculate the distance in kilometres between two coordinate pairs. For filtering, compute the distance between the searching user's coordinates and each sitter's coordinates, and return only those within the selected radius.

```python
import math

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (math.sin(d_lat / 2) ** 2 +
         math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) *
         math.sin(d_lon / 2) ** 2)
    return R * 2 * math.asin(math.sqrt(a))
```

**Map rendering:**

Pass each sitter's `latitude` and `longitude` to the OpenStreetMap frontend (e.g. Leaflet.js) as map markers. The distance filter should run server-side (or client-side if all sitters are already loaded) before markers are rendered, so only in-range sitters appear.