# Tests for profile viewing and editing
# Owner: profiles team member
#
# Areas to cover:
#   - GET /babysitter/<id>: view sitter profile (bio, rate, availability, reviews)
#   - POST /babysitter/<id>/edit: update bio, rate, availability, suburb/postcode, photo
#   - GET /parent/<id>: view parent profile (children, about, location map)
#   - POST /parent/<id>/edit: update children, about, suburb/postcode, photo
#   - Non-owners cannot edit another user's profile (403)
#   - Suburb/postcode/lat/lon saved correctly on edit

import pytest
