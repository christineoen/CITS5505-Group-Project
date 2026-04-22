from models import db
from utils import POSTCODE_SUBURB


class ParentProfile(db.Model):
    __tablename__ = "parent_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    num_children = db.Column(db.Integer)
    location = db.Column(db.String(128))
    special_requirements = db.Column(db.Text)

    user = db.relationship("User", back_populates="parent_profile")

    def to_card(self):
        return {
            "id": self.id,
            "username": self.user.username,
            "location": self.location or "",
            "suburb": POSTCODE_SUBURB.get(self.location, self.location or ""),
            "num_children": self.num_children,
            "special_requirements": self.special_requirements or "",
        }

    def __repr__(self):
        return f"<ParentProfile user_id={self.user_id}>"
