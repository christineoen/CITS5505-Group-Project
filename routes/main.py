from datetime import datetime, time as time_type
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from models import db
from models.babysitter_profile import BabysitterProfile
from models.parent_profile import ParentProfile
from models.booking import Booking
from forms import BookingForm
from utils import POSTCODE_SUBURB, DAYS

main_bp = Blueprint("main", __name__)


@main_bp.before_request
def require_profile_setup():
    if current_user.is_authenticated:
        if not current_user.is_parent and not current_user.is_babysitter:
            return redirect(url_for("auth.setup_profile"))


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


def _bookings_overlap(b1_date, b1_start, b1_duration, b2_date, b2_start, b2_duration):
    """Return True if two bookings overlap in time."""
    if b1_date != b2_date:
        return False
    b1_start_mins = b1_start.hour * 60 + b1_start.minute
    b1_end_mins = b1_start_mins + b1_duration * 60
    b2_start_mins = b2_start.hour * 60 + b2_start.minute
    b2_end_mins = b2_start_mins + b2_duration * 60
    return b1_start_mins < b2_end_mins and b2_start_mins < b1_end_mins


@main_bp.route("/booking/<int:babysitter_id>", methods=["GET", "POST"])
@login_required
def booking(babysitter_id):
    babysitter = BabysitterProfile.query.get_or_404(babysitter_id)

    if not current_user.is_parent:
        flash("You need a parent profile to make a booking.", "warning")
        return redirect(url_for("main.index"))

    parent = current_user.parent_profile

    form = BookingForm()
    if form.validate_on_submit():
        req_date = form.date.data
        req_start = form.start_time.data
        req_duration = form.duration_hours.data

        # Check for conflicting bookings for this parent (pending or accepted)
        existing = Booking.query.filter(
            Booking.parent_id == parent.id,
            Booking.status.in_(["pending", "accepted"])
        ).all()

        conflict = any(
            _bookings_overlap(req_date, req_start, req_duration,
                              b.date, b.start_time, b.duration_hours)
            for b in existing
        )

        if conflict:
            flash("You already have a pending or accepted booking that overlaps with this time slot.", "danger")
            return render_template("booking.html", babysitter=babysitter, form=form)

        new_booking = Booking(
            parent_id=parent.id,
            babysitter_id=babysitter.id,
            date=req_date,
            start_time=req_start,
            duration_hours=req_duration,
        )
        db.session.add(new_booking)
        db.session.commit()
        flash(f"Booking request sent to {babysitter.user.name}!", "success")
        return redirect(url_for("main.bookings"))

    return render_template("booking.html", babysitter=babysitter, form=form)


@main_bp.route("/bookings")
@login_required
def bookings():
    parent_bookings = {}
    babysitter_bookings = {}

    if current_user.is_parent:
        all_bookings = Booking.query.filter_by(
            parent_id=current_user.parent_profile.id
        ).order_by(Booking.date.desc(), Booking.start_time.desc()).all()

        parent_bookings = {
            "pending":   [b for b in all_bookings if b.status == "pending"],
            "accepted":  [b for b in all_bookings if b.status == "accepted"],
            "rejected":  [b for b in all_bookings if b.status == "rejected"],
            "cancelled": [b for b in all_bookings if b.status == "cancelled"],
        }

    if current_user.is_babysitter:
        all_bookings = Booking.query.filter_by(
            babysitter_id=current_user.babysitter_profile.id
        ).order_by(Booking.date.desc(), Booking.start_time.desc()).all()

        babysitter_bookings = {
            "pending":  [b for b in all_bookings if b.status == "pending"],
            "accepted": [b for b in all_bookings if b.status == "accepted"],
            "rejected": [b for b in all_bookings if b.status == "rejected"],
        }

    return render_template(
        "bookings.html",
        parent_bookings=parent_bookings,
        babysitter_bookings=babysitter_bookings,
    )


@main_bp.route("/bookings/<int:booking_id>/cancel", methods=["POST"])
@login_required
def cancel_booking(booking_id):
    b = Booking.query.get_or_404(booking_id)
    if not current_user.is_parent or b.parent_id != current_user.parent_profile.id:
        abort(403)
    if b.status != "pending":
        flash("Only pending bookings can be cancelled.", "warning")
        return redirect(url_for("main.bookings"))
    b.status = "cancelled"
    db.session.commit()
    flash("Booking cancelled.", "success")
    return redirect(url_for("main.bookings"))


@main_bp.route("/bookings/<int:booking_id>/accept", methods=["POST"])
@login_required
def accept_booking(booking_id):
    b = Booking.query.get_or_404(booking_id)
    if not current_user.is_babysitter or b.babysitter_id != current_user.babysitter_profile.id:
        abort(403)
    if b.status != "pending":
        flash("This booking is no longer pending.", "warning")
        return redirect(url_for("main.bookings"))

    # Accept this booking
    b.status = "accepted"

    # Reject all other pending bookings for this babysitter that overlap
    others = Booking.query.filter(
        Booking.babysitter_id == b.babysitter_id,
        Booking.id != b.id,
        Booking.status == "pending"
    ).all()

    for other in others:
        if _bookings_overlap(b.date, b.start_time, b.duration_hours,
                             other.date, other.start_time, other.duration_hours):
            other.status = "rejected"

    db.session.commit()
    flash("Booking accepted. Overlapping requests have been rejected.", "success")
    return redirect(url_for("main.bookings"))


@main_bp.route("/bookings/<int:booking_id>/reject", methods=["POST"])
@login_required
def reject_booking(booking_id):
    b = Booking.query.get_or_404(booking_id)
    if not current_user.is_babysitter or b.babysitter_id != current_user.babysitter_profile.id:
        abort(403)
    if b.status != "pending":
        flash("This booking is no longer pending.", "warning")
        return redirect(url_for("main.bookings"))
    b.status = "rejected"
    db.session.commit()
    flash("Booking rejected.", "success")
    return redirect(url_for("main.bookings"))


@main_bp.route("/messages")
@login_required
def messages():
    return redirect(url_for("messages.index"))


@main_bp.route("/babysitter/<int:profile_id>")
@login_required
def babysitter_profile(profile_id):
    profile = BabysitterProfile.query.get_or_404(profile_id)
    import json
    days = json.loads(profile.availability) if profile.availability else []
    return render_template("babysitter_profile.html", profile=profile, days=days)


@main_bp.route("/parent/<int:profile_id>")
@login_required
def parent_profile(profile_id):
    profile = ParentProfile.query.get_or_404(profile_id)
    is_own = current_user.is_parent and current_user.parent_profile.id == profile_id
    return render_template("parent_profile.html", profile=profile, is_own=is_own)


@main_bp.route("/parent/<int:profile_id>/edit", methods=["POST"])
@login_required
def parent_profile_edit(profile_id):
    profile = ParentProfile.query.get_or_404(profile_id)
    if not current_user.is_parent or current_user.parent_profile.id != profile_id:
        abort(403)
    profile.num_children = request.form.get("num_children", type=int)
    profile.location = request.form.get("location", "").strip() or None
    profile.special_requirements = request.form.get("special_requirements", "").strip() or None
    db.session.commit()
    flash("Profile updated.", "success")
    return redirect(url_for("main.parent_profile", profile_id=profile_id))
