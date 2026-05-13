# Tests for the messages API
# Owner: messages team member
#
# Areas to cover:
#   - GET /messages/api/conversations: returns conversations for current user
#   - GET /messages/api/conversation/<booking_id>: returns messages for a booking
#   - POST /messages/api/send: sends a message within a booking conversation
#   - PUT /messages/api/booking/<booking_id>/status: sitter accept/reject via messages API
#   - Only participants in a booking can read/send its messages (403)

import pytest
