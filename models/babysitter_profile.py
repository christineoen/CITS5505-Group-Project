import json
from models import db
from utils import POSTCODE_SUBURB


class BabysitterProfile(db.Model):
    __tablename__ = "babysitter_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    bio = db.Column(db.Text)
    hourly_rate = db.Column(db.Float)
    experience_years = db.Column(db.Integer)
    location = db.Column(db.String(128))
    availability = db.Column(db.String(256))

    user = db.relationship("User", back_populates="babysitter_profile")

    def to_card(self):
        return {
            "id": self.id,
            "username": self.user.username,
            "location": self.location or "",
            "suburb": POSTCODE_SUBURB.get(self.location, self.location or ""),
            "bio": self.bio or "",
            "hourly_rate": self.hourly_rate,
            "experience_years": self.experience_years,
            "days": json.loads(self.availability) if self.availability else [],
        }

    def __repr__(self):
        return f"<BabysitterProfile user_id={self.user_id}>"
