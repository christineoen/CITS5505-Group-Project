from flask import Blueprint, render_template
from models.user import User

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    users = User.get_all()
    return render_template("index.html", users=users)
