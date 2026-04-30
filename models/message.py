from datetime import datetime, timezone
from models import db


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey("bookings.id"), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    is_read = db.Column(db.Boolean, default=False)

    booking = db.relationship("Booking", back_populates="messages")
    sender = db.relationship("User", backref="sent_messages")

    def to_dict(self):
        return {
            "id": self.id,
            "booking_id": self.booking_id,
            "sender_id": self.sender_id,
            "sender_name": self.sender.name,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "is_read": self.is_read
        }

    def __repr__(self):
        return f"<Message {self.id} from={self.sender_id} booking={self.booking_id}>"
