from datetime import datetime, time as time_type
import os, re, uuid
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_required, current_user
from models import db
from models.babysitter_profile import BabysitterProfile
from models.parent_profile import ParentProfile
from models.booking import Booking
from forms import BookingForm, RatingForm
import json
from utils import DAYS

main_bp = Blueprint("main", __name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def _save_photo(file):
    """Save uploaded photo, return relative URL or None on failure."""
    if not file or file.filename == "":
        return None
    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return None
    filename = f"{uuid.uuid4().hex}.{ext}"
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    file.save(os.path.join(upload_folder, filename))
    return f"uploads/{filename}"


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
    
    # Get today's date for min date restriction
    today = datetime.now().date()
    
    # Get babysitter's available days
    available_days = json.loads(babysitter.availability) if babysitter.availability else []

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
            return render_template("booking.html", babysitter=babysitter, form=form, today=today, available_days=available_days)

        new_booking = Booking(
            parent_id=parent.id,
            babysitter_id=babysitter.id,
            date=req_date,
            start_time=req_start,
            duration_hours=req_duration,
            notes=form.notes.data,
        )
        db.session.add(new_booking)
        db.session.commit()
        flash(f"Booking request sent to {babysitter.user.name}!", "success")
        return redirect(url_for("main.bookings"))

    return render_template("booking.html", babysitter=babysitter, form=form, today=today, available_days=available_days)


@main_bp.route("/bookings")
@login_required
def bookings():
    from datetime import date, time as time_type, datetime as dt
    from models.rating import Rating
    parent_bookings = []
    babysitter_bookings = []
    now = dt.now()

    if current_user.is_parent:
        parent_bookings = Booking.query.filter_by(
            parent_id=current_user.parent_profile.id
        ).order_by(Booking.date.desc(), Booking.start_time.desc()).all()

    if current_user.is_babysitter:
        babysitter_bookings = Booking.query.filter_by(
            babysitter_id=current_user.babysitter_profile.id
        ).order_by(Booking.date.desc(), Booking.start_time.desc()).all()

    # Build a set of booking IDs already rated by current user
    from models.rating import Rating
    rated_booking_ids = {
        r.booking_id for r in Rating.query.filter_by(rater_id=current_user.id).all()
    }

    rating_form = RatingForm()

    return render_template(
        "bookings.html",
        parent_bookings=parent_bookings,
        babysitter_bookings=babysitter_bookings,
        now=now,
        rated_booking_ids=rated_booking_ids,
        rating_form=rating_form,
    )


@main_bp.route("/bookings/<int:booking_id>/rate", methods=["POST"])
@login_required
def rate_booking(booking_id):
    from models.rating import Rating
    b = Booking.query.get_or_404(booking_id)

    # Determine who is being rated
    if current_user.is_parent and b.parent_id == current_user.parent_profile.id:
        ratee_id = b.babysitter.user_id
    elif current_user.is_babysitter and b.babysitter_id == current_user.babysitter_profile.id:
        ratee_id = b.parent.user_id
    else:
        abort(403)

    if b.status != "completed":
        flash("You can only rate completed bookings.", "warning")
        return redirect(url_for("main.bookings"))

    # Check already rated
    if Rating.query.filter_by(booking_id=booking_id, rater_id=current_user.id).first():
        flash("You have already rated this booking.", "info")
        return redirect(url_for("main.bookings"))

    form = RatingForm()
    if form.validate_on_submit():
        rating = Rating(
            booking_id=booking_id,
            rater_id=current_user.id,
            ratee_id=ratee_id,
            score=form.score.data,
            comment=form.comment.data.strip() if form.comment.data else None,
        )
        db.session.add(rating)
        db.session.commit()
        flash("Rating submitted. Thank you!", "success")
    else:
        flash("Invalid rating. Please select a score between 1 and 5.", "danger")

    return redirect(url_for("main.bookings"))


@main_bp.route("/bookings/<int:booking_id>/complete", methods=["POST"])
@login_required
def complete_booking(booking_id):
    b = Booking.query.get_or_404(booking_id)
    if not current_user.is_parent or b.parent_id != current_user.parent_profile.id:
        abort(403)
    if b.status != "accepted":
        flash("Only accepted bookings can be marked as completed.", "warning")
        return redirect(url_for("main.bookings"))
    # Booking start must have already begun
    booking_start = datetime.combine(b.date, b.start_time)
    if datetime.now() < booking_start:
        flash("You can only complete a booking after it has started.", "warning")
        return redirect(url_for("main.bookings"))
    b.status = "completed"
    db.session.commit()
    flash("Booking marked as completed.", "success")
    return redirect(url_for("main.bookings"))


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
    flash("Booking accepted.", "success")
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


@main_bp.route("/api/pending-bookings-count")
@login_required
def pending_bookings_count():
    """API endpoint to get pending bookings count for current user"""
    from flask import jsonify
    
    count = 0
    
    if current_user.is_parent and current_user.parent_profile:
        # Parents see their sent pending requests
        count = Booking.query.filter_by(
            parent_id=current_user.parent_profile.id,
            status="pending"
        ).count()
    elif current_user.is_babysitter and current_user.babysitter_profile:
        # Babysitters see received pending requests
        count = Booking.query.filter_by(
            babysitter_id=current_user.babysitter_profile.id,
            status="pending"
        ).count()
    
    return jsonify({"count": count})


@main_bp.route("/babysitter/<int:profile_id>")
@login_required
def babysitter_profile(profile_id):
    profile = BabysitterProfile.query.get_or_404(profile_id)
    import json
    days = json.loads(profile.availability) if profile.availability else []
    is_own = current_user.is_babysitter and current_user.babysitter_profile.id == profile_id
    
    # Check if current user has any bookings with this babysitter
    has_booking = False
    if current_user.is_parent and current_user.parent_profile:
        has_booking = Booking.query.filter_by(
            parent_id=current_user.parent_profile.id,
            babysitter_id=profile_id
        ).first() is not None
    
    average_rating = profile.get_average_rating()
    rating_count = profile.get_rating_count()
    # Fetch all ratings received by this babysitter
    from models.rating import Rating
    reviews = Rating.query.filter_by(ratee_id=profile.user_id)\
                          .order_by(Rating.created_at.desc()).all()
    return render_template("babysitter_profile.html", profile=profile, days=days, is_own=is_own,
                           average_rating=average_rating, rating_count=rating_count, reviews=reviews,
                           has_booking=has_booking)


@main_bp.route("/babysitter/<int:profile_id>/edit", methods=["POST"])
@login_required
def babysitter_profile_edit(profile_id):
    profile = BabysitterProfile.query.get_or_404(profile_id)
    if not current_user.is_babysitter or current_user.babysitter_profile.id != profile_id:
        abort(403)

    bio = request.form.get("bio", "").strip() or None
    hourly_rate = request.form.get("hourly_rate", type=float)
    experience_years = request.form.get("experience_years", type=int)
    availability_days = request.form.getlist("availability")

    if hourly_rate is not None and not (0 <= hourly_rate <= 200):
        flash("Hourly rate must be between 0 and 200.", "danger")
        return redirect(url_for("main.babysitter_profile", profile_id=profile_id))

    if experience_years is not None and not (0 <= experience_years <= 50):
        flash("Experience years must be between 0 and 50.", "danger")
        return redirect(url_for("main.babysitter_profile", profile_id=profile_id))

    profile.bio = bio
    profile.hourly_rate = hourly_rate
    profile.experience_years = experience_years
    profile.availability = json.dumps(availability_days) if availability_days else None

    suburb = request.form.get("suburb", "").strip() or None
    postcode = request.form.get("postcode", "").strip() or None
    try:
        lat = float(request.form.get("lat") or "")
        lon = float(request.form.get("lon") or "")
    except (ValueError, TypeError):
        lat = lon = None

    current_user.suburb = suburb
    current_user.postcode = postcode
    current_user.latitude = lat
    current_user.longitude = lon

    photo_url = _save_photo(request.files.get("photo"))
    if photo_url:
        current_user.photo_url = photo_url

    db.session.commit()
    flash("Profile updated.", "success")
    return redirect(url_for("main.babysitter_profile", profile_id=profile_id))


@main_bp.route("/parent/<int:profile_id>")
@login_required
def parent_profile(profile_id):
    profile = ParentProfile.query.get_or_404(profile_id)
    is_own = current_user.is_parent and current_user.parent_profile.id == profile_id
    
    # Check if current user has any bookings with this parent
    has_booking = False
    if current_user.is_babysitter and current_user.babysitter_profile:
        has_booking = Booking.query.filter_by(
            parent_id=profile_id,
            babysitter_id=current_user.babysitter_profile.id
        ).first() is not None
    
    average_rating = profile.get_average_rating()
    rating_count = profile.get_rating_count()
    from models.rating import Rating
    reviews = Rating.query.filter_by(ratee_id=profile.user_id)\
                          .order_by(Rating.created_at.desc()).all()
    return render_template("parent_profile.html", profile=profile, is_own=is_own,
                           average_rating=average_rating, rating_count=rating_count, reviews=reviews,
                           has_booking=has_booking)


@main_bp.route("/parent/<int:profile_id>/edit", methods=["POST"])
@login_required
def parent_profile_edit(profile_id):
    profile = ParentProfile.query.get_or_404(profile_id)
    if not current_user.is_parent or current_user.parent_profile.id != profile_id:
        abort(403)

    profile.about = request.form.get("about", "").strip() or None

    try:
        children = json.loads(request.form.get("children_json", "[]"))
        if not isinstance(children, list):
            children = []
    except (ValueError, TypeError):
        children = []

    if len(children) > 20:
        flash("Number of children must be between 1 and 20.", "danger")
        return redirect(url_for("main.parent_profile", profile_id=profile_id))

    profile.children = children

    suburb = request.form.get("suburb", "").strip() or None
    postcode = request.form.get("postcode", "").strip() or None
    if postcode is not None:
        if not re.match(r'^\d{4}$', postcode) or not (200 <= int(postcode) <= 7999):
            flash("Please enter a valid Australian postcode.", "danger")
            return redirect(url_for("main.parent_profile", profile_id=profile_id))
    try:
        lat = float(request.form.get("lat") or "")
        lon = float(request.form.get("lon") or "")
    except (ValueError, TypeError):
        lat = lon = None

    current_user.suburb = suburb
    current_user.postcode = postcode
    current_user.latitude = lat
    current_user.longitude = lon

    photo_url = _save_photo(request.files.get("photo"))
    if photo_url:
        current_user.photo_url = photo_url

    db.session.commit()
    flash("Profile updated.", "success")
    return redirect(url_for("main.parent_profile", profile_id=profile_id))