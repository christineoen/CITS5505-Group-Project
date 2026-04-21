from flask import Blueprint, render_template
from flask_login import login_required

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    return render_template("index.html")

@main_bp.route("/about")
def about():
    return render_template("about.html")

@main_bp.route("/booking")
@login_required
def booking():
    return render_template("booking.html")

@main_bp.route("/messages")
@login_required
def messages():
    return render_template("messages.html")