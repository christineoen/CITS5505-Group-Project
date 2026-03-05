from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.user import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email    = request.form["email"]
        password = request.form["password"]  # Hash this in a real app!

        if User.get_by_username(username):
            flash("Username already taken.")
            return redirect(url_for("auth.register"))

        User.create(username, email, password)
        flash("Account created! Please log in.")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.get_by_username(username)

        if user and user["password"] == password:  # Use hashing in a real app!
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash(f"Welcome back, {username}!")
            return redirect(url_for("main.index"))

        flash("Invalid username or password.")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("main.index"))
