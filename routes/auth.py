from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from models import db
from models.user import User
from models.babysitter_profile import BabysitterProfile
from models.parent_profile import ParentProfile
from forms import RegistrationForm, LoginForm

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()
        if form.is_parent.data:
            db.session.add(ParentProfile(user_id=user.id))
        if form.is_babysitter.data:
            db.session.add(BabysitterProfile(user_id=user.id))
        db.session.commit()
        login_user(user)
        return redirect(url_for("main.index"))
    return render_template("auth/signup.html", form=form)


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
            # Guard against open redirect
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
