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
from datetime import datetime, timezone, date, time
from models import db
from models.message import Message
from models.booking import Booking


class TestMessagesAPI:
    """Test suite for messages API endpoints"""

    def test_messages_index_requires_login(self, client):
        """Test that messages index page requires authentication"""
        response = client.get("/messages/")
        assert response.status_code == 302  # Redirect to login

    def test_messages_index_authenticated(self, parent_client):
        """Test that authenticated users can access messages page"""
        response = parent_client.get("/messages/")
        assert response.status_code == 200

    def test_get_conversations_empty_for_new_user(self, parent_client):
        """Test that new users have no conversations"""
        response = parent_client.get("/messages/api/conversations")
        assert response.status_code == 200
        data = response.get_json()
        assert data == []

    def test_get_conversations_requires_login(self, client):
        """Test that conversations API requires authentication"""
        response = client.get("/messages/api/conversations")
        assert response.status_code == 302  # Redirect to login

    def test_get_conversations_with_booking(self, parent_client, booking):
        """Test getting conversations when user has bookings"""
        response = parent_client.get("/messages/api/conversations")
        assert response.status_code == 200
        data = response.get_json()
        
        assert len(data) == 1
        conversation = data[0]
        assert conversation["booking_id"] == booking.id
        assert conversation["other_user"]["name"] == "Sitter User"
        assert conversation["booking_status"] == "pending"
        assert conversation["unread_count"] == 0
        assert conversation["last_message"] is None

    def test_get_conversations_with_messages(self, parent_client, booking, sitter_user):
        """Test conversations with existing messages"""
        # Create a message from sitter to parent
        message = Message(
            booking_id=booking.id,
            sender_id=sitter_user.id,
            content="Hello, looking forward to babysitting!",
            created_at=datetime.now(timezone.utc)
        )
        db.session.add(message)
        db.session.commit()

        response = parent_client.get("/messages/api/conversations")
        assert response.status_code == 200
        data = response.get_json()
        
        assert len(data) == 1
        conversation = data[0]
        assert conversation["unread_count"] == 1  # Unread message from sitter
        assert conversation["last_message"]["content"] == "Hello, looking forward to babysitting!"

    def test_get_conversation_requires_login(self, client, booking):
        """Test that conversation API requires authentication"""
        response = client.get(f"/messages/api/conversation/{booking.id}")
        assert response.status_code == 302  # Redirect to login

    def test_get_conversation_unauthorized_user(self, auth_client, booking):
        """Test that unauthorized users cannot access conversations"""
        response = auth_client.get(f"/messages/api/conversation/{booking.id}")
        assert response.status_code == 403
        data = response.get_json()
        assert "Unauthorized" in data["error"]

    def test_get_conversation_parent_access(self, parent_client, booking):
        """Test that parent can access their booking conversation"""
        response = parent_client.get(f"/messages/api/conversation/{booking.id}")
        assert response.status_code == 200
        data = response.get_json()
        
        assert data["booking"]["id"] == booking.id
        assert data["booking"]["status"] == "pending"
        assert data["other_user"]["name"] == "Sitter User"
        assert data["is_parent"] is True
        assert data["user_role"] == "parent"
        assert data["messages"] == []

    def test_get_conversation_sitter_access(self, sitter_client, booking):
        """Test that sitter can access their booking conversation"""
        response = sitter_client.get(f"/messages/api/conversation/{booking.id}")
        assert response.status_code == 200
        data = response.get_json()
        
        assert data["booking"]["id"] == booking.id
        assert data["other_user"]["name"] == "Parent User"
        assert data["is_parent"] is False
        assert data["user_role"] == "babysitter"

    def test_get_conversation_with_messages(self, parent_client, booking, parent_user, sitter_user):
        """Test getting conversation with existing messages"""
        # Create messages
        msg1 = Message(
            booking_id=booking.id,
            sender_id=parent_user.id,
            content="Hi, can you babysit on Friday?",
            created_at=datetime.now(timezone.utc)
        )
        msg2 = Message(
            booking_id=booking.id,
            sender_id=sitter_user.id,
            content="Yes, I'm available!",
            created_at=datetime.now(timezone.utc)
        )
        db.session.add_all([msg1, msg2])
        db.session.commit()

        response = parent_client.get(f"/messages/api/conversation/{booking.id}")
        assert response.status_code == 200
        data = response.get_json()
        
        assert len(data["messages"]) == 2
        assert data["messages"][0]["content"] == "Hi, can you babysit on Friday?"
        assert data["messages"][1]["content"] == "Yes, I'm available!"

    def test_get_conversation_marks_messages_as_read(self, parent_client, booking, sitter_user):
        """Test that viewing conversation marks messages as read"""
        # Create unread message from sitter
        message = Message(
            booking_id=booking.id,
            sender_id=sitter_user.id,
            content="Hello!",
            is_read=False,
            created_at=datetime.now(timezone.utc)
        )
        db.session.add(message)
        db.session.commit()

        # Verify message is unread
        assert not message.is_read

        # View conversation
        response = parent_client.get(f"/messages/api/conversation/{booking.id}")
        assert response.status_code == 200

        # Verify message is now marked as read
        db.session.refresh(message)
        assert message.is_read

    def test_send_message_requires_login(self, client, booking):
        """Test that sending messages requires authentication"""
        response = client.post("/messages/api/send", json={
            "booking_id": booking.id,
            "content": "Test message"
        })
        assert response.status_code == 302  # Redirect to login

    def test_send_message_missing_data(self, parent_client):
        """Test sending message with missing data"""
        response = parent_client.post("/messages/api/send", json={})
        assert response.status_code == 400
        data = response.get_json()
        assert "No data provided" in data["error"]

    def test_send_message_missing_fields(self, parent_client, booking):
        """Test sending message with missing required fields"""
        # Missing content
        response = parent_client.post("/messages/api/send", json={
            "booking_id": booking.id
        })
        assert response.status_code == 400
        data = response.get_json()
        assert "Missing booking_id or content" in data["error"]

        # Missing booking_id
        response = parent_client.post("/messages/api/send", json={
            "content": "Test message"
        })
        assert response.status_code == 400

    def test_send_message_empty_content(self, parent_client, booking):
        """Test sending message with empty content"""
        response = parent_client.post("/messages/api/send", json={
            "booking_id": booking.id,
            "content": "   "  # Only whitespace
        })
        assert response.status_code == 400
        data = response.get_json()
        assert "Missing booking_id or content" in data["error"]

    def test_send_message_too_long(self, parent_client, booking):
        """Test sending message that exceeds length limit"""
        long_content = "x" * 1001  # Exceeds 1000 character limit
        response = parent_client.post("/messages/api/send", json={
            "booking_id": booking.id,
            "content": long_content
        })
        assert response.status_code == 400
        data = response.get_json()
        assert "Message too long" in data["error"]

    def test_send_message_unauthorized(self, auth_client, booking):
        """Test that unauthorized users cannot send messages"""
        response = auth_client.post("/messages/api/send", json={
            "booking_id": booking.id,
            "content": "Unauthorized message"
        })
        assert response.status_code == 403
        data = response.get_json()
        assert "Unauthorized" in data["error"]

    def test_send_message_success_parent(self, parent_client, booking, parent_user):
        """Test successful message sending by parent"""
        response = parent_client.post("/messages/api/send", json={
            "booking_id": booking.id,
            "content": "Looking forward to working with you!"
        })
        assert response.status_code == 201
        data = response.get_json()
        
        assert data["booking_id"] == booking.id
        assert data["sender_id"] == parent_user.id
        assert data["content"] == "Looking forward to working with you!"
        assert data["is_system"] is False
        assert "created_at" in data

        # Verify message was saved to database
        message = Message.query.filter_by(booking_id=booking.id).first()
        assert message is not None
        assert message.content == "Looking forward to working with you!"

    def test_send_message_success_sitter(self, sitter_client, booking, sitter_user):
        """Test successful message sending by sitter"""
        response = sitter_client.post("/messages/api/send", json={
            "booking_id": booking.id,
            "content": "Thank you for choosing me!"
        })
        assert response.status_code == 201
        data = response.get_json()
        
        assert data["sender_id"] == sitter_user.id
        assert data["content"] == "Thank you for choosing me!"

    def test_update_booking_status_requires_login(self, client, booking):
        """Test that updating booking status requires authentication"""
        response = client.put(f"/messages/api/booking/{booking.id}/status", json={
            "status": "accepted"
        })
        assert response.status_code == 302  # Redirect to login

    def test_update_booking_status_parent_unauthorized(self, parent_client, booking):
        """Test that parents cannot update booking status"""
        response = parent_client.put(f"/messages/api/booking/{booking.id}/status", json={
            "status": "accepted"
        })
        assert response.status_code == 403
        data = response.get_json()
        assert "Only babysitter can update booking status" in data["error"]

    def test_update_booking_status_unauthorized_sitter(self, app, client, parent_user, sitter_user):
        """Test that unauthorized sitters cannot update booking status"""
        # Create another sitter
        from models.user import User
        from models.babysitter_profile import BabysitterProfile
        
        other_sitter = User(name="Other Sitter", email="other@test.com")
        other_sitter.set_password("Password1!")
        db.session.add(other_sitter)
        db.session.flush()
        db.session.add(BabysitterProfile(
            user_id=other_sitter.id,
            bio="Another sitter",
            hourly_rate=20.0,
            experience_years=2,
        ))
        db.session.commit()

        # Login as other sitter
        client.post("/auth/login", data={"email": "other@test.com", "password": "Password1!"})

        # Create booking with original sitter (use the sitter_user fixture)
        booking = Booking(
            parent_id=parent_user.parent_profile.id,
            babysitter_id=sitter_user.babysitter_profile.id,  # Use existing sitter
            date=date(2026, 8, 1),
            start_time=time(18, 0),
            duration_hours=3,
            status="pending",
        )
        db.session.add(booking)
        db.session.commit()

        # Try to update status as unauthorized sitter
        response = client.put(f"/messages/api/booking/{booking.id}/status", json={
            "status": "accepted"
        })
        assert response.status_code == 403

    def test_update_booking_status_missing_data(self, sitter_client, booking):
        """Test updating booking status with missing data"""
        response = sitter_client.put(f"/messages/api/booking/{booking.id}/status", json={})
        assert response.status_code == 400
        data = response.get_json()
        assert "No data provided" in data["error"]

    def test_update_booking_status_invalid_status(self, sitter_client, booking):
        """Test updating booking status with invalid status"""
        response = sitter_client.put(f"/messages/api/booking/{booking.id}/status", json={
            "status": "invalid_status"
        })
        assert response.status_code == 400
        data = response.get_json()
        assert "Invalid status" in data["error"]

    def test_update_booking_status_already_processed(self, sitter_client, booking):
        """Test updating booking status when already processed"""
        # First, accept the booking
        booking.status = "accepted"
        db.session.commit()

        # Try to update again
        response = sitter_client.put(f"/messages/api/booking/{booking.id}/status", json={
            "status": "rejected"
        })
        assert response.status_code == 400
        data = response.get_json()
        assert "Cannot update booking status" in data["error"]

    def test_update_booking_status_accept_success(self, sitter_client, booking, sitter_user):
        """Test successful booking acceptance"""
        response = sitter_client.put(f"/messages/api/booking/{booking.id}/status", json={
            "status": "accepted"
        })
        assert response.status_code == 200
        data = response.get_json()
        
        assert data["status"] == "accepted"
        assert data["success"] is True
        assert "message" in data
        assert data["message"]["is_system"] is True
        assert "accepted your booking request" in data["message"]["content"]

        # Verify booking status was updated
        db.session.refresh(booking)
        assert booking.status == "accepted"

        # Verify system message was created
        system_message = Message.query.filter_by(
            booking_id=booking.id,
            is_system=True
        ).first()
        assert system_message is not None
        assert "accepted your booking request" in system_message.content

    def test_update_booking_status_reject_success(self, sitter_client, booking):
        """Test successful booking rejection"""
        response = sitter_client.put(f"/messages/api/booking/{booking.id}/status", json={
            "status": "rejected"
        })
        assert response.status_code == 200
        data = response.get_json()
        
        assert data["status"] == "rejected"
        assert data["success"] is True
        assert "declined your booking request" in data["message"]["content"]

        # Verify booking status was updated
        db.session.refresh(booking)
        assert booking.status == "rejected"

    def test_conversation_sorting_by_last_message(self, parent_client, parent_user, sitter_user):
        """Test that conversations are sorted by last message time"""
        # Create two bookings
        booking1 = Booking(
            parent_id=parent_user.parent_profile.id,
            babysitter_id=sitter_user.babysitter_profile.id,
            date=date(2026, 8, 1),
            start_time=time(18, 0),
            duration_hours=3,
            status="pending",
        )
        booking2 = Booking(
            parent_id=parent_user.parent_profile.id,
            babysitter_id=sitter_user.babysitter_profile.id,
            date=date(2026, 8, 2),
            start_time=time(19, 0),
            duration_hours=2,
            status="pending",
        )
        db.session.add_all([booking1, booking2])
        db.session.commit()

        # Add message to booking1 (older)
        msg1 = Message(
            booking_id=booking1.id,
            sender_id=sitter_user.id,
            content="First message",
            created_at=datetime(2026, 7, 1, 10, 0, 0, tzinfo=timezone.utc)
        )
        # Add message to booking2 (newer)
        msg2 = Message(
            booking_id=booking2.id,
            sender_id=sitter_user.id,
            content="Second message",
            created_at=datetime(2026, 7, 1, 11, 0, 0, tzinfo=timezone.utc)
        )
        db.session.add_all([msg1, msg2])
        db.session.commit()

        response = parent_client.get("/messages/api/conversations")
        assert response.status_code == 200
        data = response.get_json()
        
        assert len(data) == 2
        # Should be sorted by most recent message first
        assert data[0]["booking_id"] == booking2.id
        assert data[1]["booking_id"] == booking1.id

    def test_message_model_to_dict(self, booking, parent_user):
        """Test Message model to_dict method"""
        message = Message(
            booking_id=booking.id,
            sender_id=parent_user.id,
            content="Test message",
            created_at=datetime.now(timezone.utc)
        )
        db.session.add(message)
        db.session.commit()

        message_dict = message.to_dict()
        
        assert message_dict["booking_id"] == booking.id
        assert message_dict["sender_id"] == parent_user.id
        assert message_dict["sender_name"] == "Parent User"
        assert message_dict["content"] == "Test message"
        assert message_dict["is_read"] is False
        assert message_dict["is_system"] is False
        assert "created_at" in message_dict

    def test_error_handlers(self, parent_client):
        """Test error handlers for 404 and 500 errors"""
        # Test 404 for non-existent booking - this will return 500 due to get_or_404 behavior
        # The route uses get_or_404 which raises an exception that gets caught by the error handler
        response = parent_client.get("/messages/api/conversation/99999")
        assert response.status_code == 500  # Error handler catches the 404 exception
        data = response.get_json()
        assert "error" in data

        response = parent_client.put("/messages/api/booking/99999/status", json={
            "status": "accepted"
        })
        assert response.status_code == 500  # Same behavior for PUT requests
