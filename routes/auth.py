import json
import urllib.request
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse, quote
from models import db
from models.user import User
from models.babysitter_profile import BabysitterProfile
from models.parent_profile import ParentProfile
from forms import RegistrationForm, LoginForm, ProfileDetailsForm
from utils import DAYS, POSTCODE_SUBURB, geocode_suburb

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

_VALID_ROLES = ("parent", "sitter")


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(name=form.name.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for("auth.setup_profile"))
    return render_template("auth/signup.html", form=form)


@auth_bp.route("/setup-profile", methods=["GET", "POST"])
@login_required
def setup_profile():
    if current_user.is_parent or current_user.is_babysitter:
        return redirect(url_for("main.index"))
    if request.method == "POST":
        role = request.form.get("role")
        if role in _VALID_ROLES:
            session["pending_role"] = role
            return redirect(url_for("auth.setup_profile_details"))
    pending_role = session.get("pending_role")
    return render_template("auth/setup_profile.html", pending_role=pending_role)


@auth_bp.route("/setup-profile/details", methods=["GET", "POST"])
@login_required
def setup_profile_details():
    if current_user.is_parent or current_user.is_babysitter:
        return redirect(url_for("main.index"))
    role = session.get("pending_role")
    if role not in _VALID_ROLES:
        return redirect(url_for("auth.setup_profile"))

    form = ProfileDetailsForm()
    if form.validate_on_submit():
        current_user.suburb = form.suburb.data or None
        current_user.postcode = form.postcode.data or None
        lat, lng = geocode_suburb(form.suburb.data, form.postcode.data)
        current_user.latitude = lat
        current_user.longitude = lng

        if role == "parent":
            try:
                children = json.loads(form.children_json.data) if form.children_json.data else []
                if not isinstance(children, list):
                    children = []
            except (ValueError, TypeError):
                children = []
            db.session.add(ParentProfile(
                user_id=current_user.id,
                about=form.about.data or None,
                children=children,
            ))
        else:
            db.session.add(BabysitterProfile(
                user_id=current_user.id,
                bio=form.bio.data or None,
                hourly_rate=form.hourly_rate.data,
                experience_years=form.experience_years.data,
                availability=json.dumps(form.availability.data) if form.availability.data else None,
            ))

        session.pop("pending_role", None)
        db.session.commit()
        return redirect(url_for("main.index"))

    template = "auth/setup_parent.html" if role == "parent" else "auth/setup_sitter.html"
    return render_template(template, form=form, days=DAYS)


@auth_bp.route("/postcode-search")
def postcode_search():
    q = request.args.get("q", "").strip()
    if len(q) < 2:
        return jsonify([])

    results = []
    seen = set()
    q_lower = q.lower()

    # Search local dict by postcode prefix or suburb name prefix
    for postcode, suburb in POSTCODE_SUBURB.items():
        if postcode.startswith(q) or suburb.lower().startswith(q_lower):
            key = (postcode, suburb)
            if key not in seen:
                seen.add(key)
                results.append({"suburb": suburb, "postcode": postcode})

    if len(results) < 8:
        try:
            url = (
                f"https://nominatim.openstreetmap.org/search"
                f"?q={quote(q)}&countrycodes=au&format=json&addressdetails=1&limit=10"
            )
            req = urllib.request.Request(url, headers={"User-Agent": "SitBuddy/1.0"})
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read())
            for item in data:
                addr = item.get("address", {})
                postcode = addr.get("postcode", "")
                suburb = (
                    addr.get("suburb")
                    or addr.get("city_district")
                    or addr.get("town")
                    or addr.get("village")
                    or addr.get("city")
                    or ""
                )
                if not postcode or not suburb:
                    continue
                key = (postcode, suburb)
                if key not in seen:
                    seen.add(key)
                    results.append({"suburb": suburb, "postcode": postcode})
        except Exception:
            pass

    return jsonify(results[:8])


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            if next_page and urlparse(next_page).netloc:
                next_page = None
            return redirect(next_page or url_for("main.index"))
        flash("Invalid email or password.", "danger")
    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))
