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
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    parent = db.relationship("ParentProfile", backref="bookings")
    babysitter = db.relationship("BabysitterProfile", backref="bookings")

    def __repr__(self):
        return f"<Booking parent={self.parent_id} babysitter={self.babysitter_id} date={self.date}>"
