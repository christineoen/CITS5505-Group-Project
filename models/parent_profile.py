from models import db


class ParentProfile(db.Model):
    __tablename__ = "parent_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    num_children = db.Column(db.Integer)
    location = db.Column(db.String(128))
    special_requirements = db.Column(db.Text)

    user = db.relationship("User", back_populates="parent_profile")

    def __repr__(self):
        return f"<ParentProfile user_id={self.user_id}>"
