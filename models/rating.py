from datetime import datetime, timezone
from models import db


class Rating(db.Model):
    __tablename__ = "ratings"

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey("bookings.id"), nullable=False)
    rater_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    ratee_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    score = db.Column(db.Integer, nullable=False)  # 1-5
    comment = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    booking = db.relationship("Booking", backref="ratings")
    rater = db.relationship("User", foreign_keys=[rater_id], backref="ratings_given")
    ratee = db.relationship("User", foreign_keys=[ratee_id], backref="ratings_received")

    __table_args__ = (
        db.UniqueConstraint("booking_id", "rater_id", name="unique_rating_per_user_per_booking"),
    )

    def __repr__(self):
        return f"<Rating {self.id} booking={self.booking_id} score={self.score}>"
