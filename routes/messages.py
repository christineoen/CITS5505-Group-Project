"""
Messages Blueprint - Handles messaging functionality between parents and babysitters
"""
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models import db
from models.booking import Booking
from models.message import Message
from models.user import User
from datetime import datetime, timezone
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

messages_bp = Blueprint("messages", __name__, url_prefix="/messages")


@messages_bp.route("/")
@login_required
def index():
    """Display messages page"""
    return render_template("messages.html")


@messages_bp.route("/api/conversations")
@login_required
def get_conversations():
    """Get all conversation list for current user with enhanced error handling"""
    try:
        # Get all bookings where current user is parent or babysitter
        bookings = []
        if current_user.is_parent and current_user.parent_profile:
            bookings = Booking.query.filter_by(parent_id=current_user.parent_profile.id).all()
        elif current_user.is_babysitter and current_user.babysitter_profile:
            bookings = Booking.query.filter_by(babysitter_id=current_user.babysitter_profile.id).all()
        
        if not bookings:
            return jsonify([])

        conversations = []
        for booking in bookings:
            try:
                # Determine the other party in the conversation
                if current_user.parent_profile and booking.parent_id == current_user.parent_profile.id:
                    other_user = booking.babysitter.user
                else:
                    other_user = booking.parent.user

                # Get last message
                last_message = Message.query.filter_by(booking_id=booking.id)\
                    .order_by(Message.created_at.desc()).first()
                
                # Get unread message count
                unread_count = Message.query.filter_by(
                    booking_id=booking.id,
                    is_read=False
                ).filter(Message.sender_id != current_user.id).count()

                # Calculate end time
                from datetime import datetime, timedelta
                start_datetime = datetime.combine(booking.date, booking.start_time)
                end_datetime = start_datetime + timedelta(hours=booking.duration_hours)

                conversations.append({
                    "booking_id": booking.id,
                    "other_user": {
                        "id": other_user.id,
                        "name": other_user.name
                    },
                    "booking_status": booking.status,
                    "booking_date": booking.date.strftime('%a, %-d %b %Y'),
                    "booking_time": f"{booking.start_time.strftime('%-I:%M %p')} - {end_datetime.strftime('%-I:%M %p')}",
                    "last_message": last_message.to_dict() if last_message else None,
                    "unread_count": unread_count
                })
            except Exception as e:
                logger.error(f"Error processing booking {booking.id}: {str(e)}")
                continue

        # Sort by last message time (most recent first)
        conversations.sort(
            key=lambda x: x["last_message"]["created_at"] if x["last_message"] else "1970-01-01", 
            reverse=True
        )
        
        return jsonify(conversations)
        
    except Exception as e:
        logger.error(f"Error in get_conversations: {str(e)}")
        return jsonify({"error": "Failed to load conversations"}), 500


@messages_bp.route("/api/conversation/<int:booking_id>")
@login_required
def get_conversation(booking_id):
    """Get all messages for a specific booking with role information"""
    try:
        booking = Booking.query.get_or_404(booking_id)
        
        # Verify user has permission to view this conversation
        user_parent_id = current_user.parent_profile.id if current_user.parent_profile else None
        user_babysitter_id = current_user.babysitter_profile.id if current_user.babysitter_profile else None
        
        if booking.parent_id != user_parent_id and booking.babysitter_id != user_babysitter_id:
            return jsonify({"error": "Unauthorized"}), 403

        # Mark all messages as read
        Message.query.filter_by(booking_id=booking_id).filter(
            Message.sender_id != current_user.id,
            Message.is_read == False
        ).update({"is_read": True})
        db.session.commit()

        # Get all messages
        messages = Message.query.filter_by(booking_id=booking_id).order_by(Message.created_at.asc()).all()
        
        # Determine the other party in the conversation
        if user_parent_id and booking.parent_id == user_parent_id:
            other_user = booking.babysitter.user
            is_parent = True
        else:
            other_user = booking.parent.user
            is_parent = False

        # Calculate end time
        from datetime import datetime, timedelta
        start_datetime = datetime.combine(booking.date, booking.start_time)
        end_datetime = start_datetime + timedelta(hours=booking.duration_hours)

        return jsonify({
            "booking": {
                "id": booking.id,
                "status": booking.status,
                "date": booking.date.strftime('%a, %-d %b %Y'),
                "time": f"{booking.start_time.strftime('%-I:%M %p')} - {end_datetime.strftime('%-I:%M %p')}"
            },
            "other_user": {
                "id": other_user.id,
                "name": other_user.name
            },
            "messages": [msg.to_dict() for msg in messages],
            "is_parent": is_parent,
            "user_role": "parent" if is_parent else "babysitter"
        })
        
    except Exception as e:
        logger.error(f"Error in get_conversation: {str(e)}")
        return jsonify({"error": "Failed to load conversation"}), 500


@messages_bp.route("/api/send", methods=["POST"])
@login_required
def send_message():
    """Send new message with enhanced validation"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        booking_id = data.get("booking_id")
        content = data.get("content", "").strip()

        if not booking_id or not content:
            return jsonify({"error": "Missing booking_id or content"}), 400

        # Validate content length
        if len(content) > 1000:
            return jsonify({"error": "Message too long (max 1000 characters)"}), 400

        booking = Booking.query.get_or_404(booking_id)
        
        # Verify user has permission to send message
        user_parent_id = current_user.parent_profile.id if current_user.parent_profile else None
        user_babysitter_id = current_user.babysitter_profile.id if current_user.babysitter_profile else None
        
        if booking.parent_id != user_parent_id and booking.babysitter_id != user_babysitter_id:
            return jsonify({"error": "Unauthorized"}), 403

        # Create new message
        message = Message(
            booking_id=booking_id,
            sender_id=current_user.id,
            content=content,
            created_at=datetime.now(timezone.utc)  # Explicitly set UTC time
        )
        db.session.add(message)
        db.session.commit()

        logger.info(f"Message sent: user={current_user.id}, booking={booking_id}")
        return jsonify(message.to_dict()), 201
        
    except Exception as e:
        logger.error(f"Error in send_message: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "Failed to send message"}), 500


@messages_bp.route("/api/booking/<int:booking_id>/status", methods=["PUT"])
@login_required
def update_booking_status(booking_id):
    """Update booking status with enhanced system messages"""
    try:
        booking = Booking.query.get_or_404(booking_id)
        
        # Only babysitter can accept or reject booking
        user_babysitter_id = current_user.babysitter_profile.id if current_user.babysitter_profile else None
        if booking.babysitter_id != user_babysitter_id:
            return jsonify({"error": "Unauthorized - Only babysitter can update booking status"}), 403

        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        new_status = data.get("status")

        if new_status not in ["accepted", "rejected"]:
            return jsonify({"error": "Invalid status. Must be 'accepted' or 'rejected'"}), 400

        # Check if booking is still pending
        if booking.status != "pending":
            return jsonify({"error": f"Cannot update booking status. Current status is '{booking.status}'"}), 400

        # Update booking status
        old_status = booking.status
        booking.status = new_status
        booking.updated_at = datetime.now()
        
        # Create enhanced system message
        status_messages = {
            "accepted": (
                f"🎉 Great news! {current_user.name} has accepted your booking request "
                f"for {booking.date.strftime('%B %d, %Y')} at {booking.start_time.strftime('%I:%M %p')}. "
                f"Looking forward to babysitting!"
            ),
            "rejected": (
                f"😔 {current_user.name} has declined your booking request "
                f"for {booking.date.strftime('%B %d, %Y')} at {booking.start_time.strftime('%I:%M %p')}. "
                f"Please try booking another babysitter or different time."
            )
        }
        
        system_message_content = status_messages.get(new_status, f"Booking has been {new_status}.")
        
        system_message = Message(
            booking_id=booking_id,
            sender_id=current_user.id,
            content=system_message_content,
            is_system=True,
            created_at=datetime.now(timezone.utc)
        )
        
        db.session.add(system_message)
        db.session.commit()

        logger.info(f"Booking status updated: booking={booking_id}, status={new_status}, user={current_user.id}")
        
        return jsonify({
            "status": booking.status,
            "message": system_message.to_dict(),
            "success": True
        })
        
    except Exception as e:
        logger.error(f"Error in update_booking_status: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "Failed to update booking status"}), 500


@messages_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Resource not found"}), 404


@messages_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    db.session.rollback()
    return jsonify({"error": "Internal server error"}), 500
