"""
Message Model - Represents messages in conversations between users
"""
from datetime import datetime, timezone
from models import db


class Message(db.Model):
    """Message model for storing conversation messages"""
    
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey("bookings.id"), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    is_read = db.Column(db.Boolean, default=False)
    is_system = db.Column(db.Boolean, default=False)

    # Relationships
    booking = db.relationship("Booking", back_populates="messages")
    sender = db.relationship("User", backref="sent_messages")

    def to_dict(self):
        """Convert message to dictionary for JSON serialization"""
        # Ensure proper timezone handling
        local_time = self.created_at
        if self.created_at.tzinfo is None:
            # If no timezone info, assume UTC
            local_time = self.created_at.replace(tzinfo=timezone.utc)
        
        return {
            "id": self.id,
            "booking_id": self.booking_id,
            "sender_id": self.sender_id,
            "sender_name": self.sender.name,
            "content": self.content,
            "created_at": local_time.isoformat(),
            "is_read": self.is_read,
            "is_system": self.is_system
        }

    def __repr__(self):
        return (
            f"<Message {self.id} from={self.sender_id} "
            f"booking={self.booking_id} system={self.is_system}>"
        )
