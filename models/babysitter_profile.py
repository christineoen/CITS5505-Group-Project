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
    availability = db.Column(db.String(256))

    user = db.relationship("User", back_populates="babysitter_profile")

    def get_average_rating(self):
        from models.rating import Rating
        from sqlalchemy import func
        result = db.session.query(func.avg(Rating.score)).filter_by(ratee_id=self.user_id).scalar()
        return round(float(result), 1) if result else None

    def get_rating_count(self):
        from models.rating import Rating
        return Rating.query.filter_by(ratee_id=self.user_id).count()

    def to_card(self):
        postcode = self.user.postcode or ""
        suburb = self.user.suburb or POSTCODE_SUBURB.get(postcode, "")
        return {
            "id": self.id,
            "name": self.user.name,
            "location": postcode,
            "suburb": suburb,
            "bio": self.bio or "",
            "hourly_rate": self.hourly_rate,
            "experience_years": self.experience_years,
            "days": json.loads(self.availability) if self.availability else [],
            "lat": self.user.latitude,
            "lng": self.user.longitude,
            "average_rating": self.get_average_rating(),
            "rating_count": self.get_rating_count(),
        }

    def __repr__(self):
        return f"<BabysitterProfile user_id={self.user_id}>"
