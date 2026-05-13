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
