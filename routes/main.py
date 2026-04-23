from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db
from models.babysitter_profile import BabysitterProfile
from models.parent_profile import ParentProfile
from models.booking import Booking
from forms import BookingForm
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


@main_bp.route("/booking/<int:babysitter_id>", methods=["GET", "POST"])
@login_required
def booking(babysitter_id):
    babysitter = BabysitterProfile.query.get_or_404(babysitter_id)

    if not current_user.is_parent:
        flash("You need a parent profile to make a booking.", "warning")
        return redirect(url_for("main.index"))

    form = BookingForm()
    if form.validate_on_submit():
        new_booking = Booking(
            parent_id=current_user.parent_profile.id,
            babysitter_id=babysitter.id,
            date=form.date.data,
            start_time=form.start_time.data,
            duration_hours=form.duration_hours.data,
        )
        db.session.add(new_booking)
        db.session.commit()
        flash(f"Booking request sent to {babysitter.user.username}!", "success")
        return redirect(url_for("main.index"))

    return render_template("booking.html", babysitter=babysitter, form=form)


@main_bp.route("/messages")
@login_required
def messages():
    return redirect(url_for("messages.index"))

@main_bp.route("/babysitter/<int:profile_id>")
@login_required
def babysitter_profile(profile_id):
    return render_template("babysitter_profile.html")

@main_bp.route("/parent/<int:profile_id>")
@login_required
def parent_profile(profile_id):
    return render_template("parent_profile.html")