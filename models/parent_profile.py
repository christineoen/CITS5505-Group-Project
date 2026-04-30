from models import db
from utils import POSTCODE_SUBURB


class ParentProfile(db.Model):
    __tablename__ = "parent_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    children = db.Column(db.JSON, default=list)
    about = db.Column(db.Text)

    user = db.relationship("User", back_populates="parent_profile")

    def to_card(self):
        postcode = self.user.postcode or ""
        suburb = self.user.suburb or POSTCODE_SUBURB.get(postcode, "")
        return {
            "id": self.id,
            "name": self.user.name,
            "location": postcode,
            "suburb": suburb,
            "num_children": len(self.children) if self.children else 0,
            "about": self.about or "",
            "lat": self.user.latitude,
            "lng": self.user.longitude,
        }

    def __repr__(self):
        return f"<ParentProfile user_id={self.user_id}>"
