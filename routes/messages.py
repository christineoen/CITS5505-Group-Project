from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models import db
from models.booking import Booking
from models.message import Message
from models.user import User
from datetime import datetime

messages_bp = Blueprint("messages", __name__, url_prefix="/messages")


@messages_bp.route("/")
@login_required
def index():
    """Display messages page"""
    return render_template("messages.html")


@messages_bp.route("/api/conversations")
@login_required
def get_conversations():
    """Get all conversation list for current user"""
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
        # Determine the other party in the conversation
        if current_user.parent_profile and booking.parent_id == current_user.parent_profile.id:
            other_user = booking.babysitter.user
        else:
            other_user = booking.parent.user

        # Get last message
        last_message = Message.query.filter_by(booking_id=booking.id).order_by(Message.created_at.desc()).first()
        
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
            "booking_date": booking.date.isoformat(),
            "booking_time": f"{booking.start_time.strftime('%H:%M')} - {end_datetime.strftime('%H:%M')}",
            "last_message": last_message.to_dict() if last_message else None,
            "unread_count": unread_count
        })

    # Sort by last message time
    conversations.sort(key=lambda x: x["last_message"]["created_at"] if x["last_message"] else "", reverse=True)
    
    return jsonify(conversations)


@messages_bp.route("/api/conversation/<int:booking_id>")
@login_required
def get_conversation(booking_id):
    """Get all messages for a specific booking"""
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
    else:
        other_user = booking.parent.user

    # Calculate end time
    from datetime import datetime, timedelta
    start_datetime = datetime.combine(booking.date, booking.start_time)
    end_datetime = start_datetime + timedelta(hours=booking.duration_hours)

    return jsonify({
        "booking": {
            "id": booking.id,
            "status": booking.status,
            "date": booking.date.isoformat(),
            "time": f"{booking.start_time.strftime('%H:%M')} - {end_datetime.strftime('%H:%M')}"
        },
        "other_user": {
            "id": other_user.id,
            "name": other_user.name
        },
        "messages": [msg.to_dict() for msg in messages]
    })


@messages_bp.route("/api/send", methods=["POST"])
@login_required
def send_message():
    """Send new message"""
    data = request.get_json()
    booking_id = data.get("booking_id")
    content = data.get("content", "").strip()

    if not booking_id or not content:
        return jsonify({"error": "Missing booking_id or content"}), 400

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
        content=content
    )
    db.session.add(message)
    db.session.commit()

    return jsonify(message.to_dict()), 201


@messages_bp.route("/api/booking/<int:booking_id>/status", methods=["PUT"])
@login_required
def update_booking_status(booking_id):
    """Update booking status (accept/reject)"""
    booking = Booking.query.get_or_404(booking_id)
    
    # Only babysitter can accept or reject booking
    user_babysitter_id = current_user.babysitter_profile.id if current_user.babysitter_profile else None
    if booking.babysitter_id != user_babysitter_id:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    new_status = data.get("status")

    if new_status not in ["accepted", "rejected"]:
        return jsonify({"error": "Invalid status"}), 400

    booking.status = new_status
    booking.updated_at = datetime.now()
    db.session.commit()

    # Automatically send system message
    system_message_content = f"Booking has been {new_status}."
    system_message = Message(
        booking_id=booking_id,
        sender_id=current_user.id,
        content=system_message_content
    )
    db.session.add(system_message)
    db.session.commit()

    return jsonify({"status": booking.status, "message": system_message.to_dict()})
