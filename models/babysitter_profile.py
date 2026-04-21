from models import db


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

    def __repr__(self):
        return f"<BabysitterProfile user_id={self.user_id}>"
