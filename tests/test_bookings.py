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

import pytest
