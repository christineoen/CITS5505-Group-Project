from datetime import datetime, timezone
from models import db


class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey("parent_profiles.id"), nullable=False)
    babysitter_id = db.Column(db.Integer, db.ForeignKey("babysitter_profiles.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    duration_hours = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default="pending")  # pending, accepted, rejected, completed
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    parent = db.relationship("ParentProfile", backref="bookings")
    babysitter = db.relationship("BabysitterProfile", backref="bookings")
    messages = db.relationship("Message", back_populates="booking", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Booking {self.id} parent={self.parent_id} babysitter={self.babysitter_id} status={self.status}>"
