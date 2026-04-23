from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models.babysitter_profile import BabysitterProfile
from models.parent_profile import ParentProfile
from utils import POSTCODE_SUBURB, DAYS

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    mode = None
    profiles = []
    locations = []

    if current_user.is_authenticated:
        if current_user.is_parent:
            mode = "babysitters"
            profiles = [p.to_card() for p in BabysitterProfile.query.join(BabysitterProfile.user).all()]
        elif current_user.is_babysitter:
            mode = "parents"
            profiles = [p.to_card() for p in ParentProfile.query.join(ParentProfile.user).all()]
        locations = sorted({p["location"] for p in profiles if p["location"]})

    return render_template(
        "index.html",
        mode=mode,
        profiles=profiles,
        locations=locations,
        postcode_suburb=POSTCODE_SUBURB,
        days=DAYS,
    )


@main_bp.route("/booking")
@login_required
def booking():
    return render_template("booking.html")


@main_bp.route("/messages")
@login_required
def messages():
    return render_template("messages.html")

@main_bp.route("/babysitter/<int:profile_id>")
@login_required
def babysitter_profile(profile_id):
    return render_template("babysitter_profile.html")

@main_bp.route("/parent/<int:profile_id>")
@login_required
def parent_profile(profile_id):
    return render_template("parent_profile.html")