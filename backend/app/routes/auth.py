from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    request,
    flash,
    current_app,
)
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User
from datetime import datetime

auth = Blueprint("auth", __name__)


@auth.route("/")
def index():
    if current_user.is_authenticated:
        if not current_user.onboarding_complete:
            return redirect(url_for("auth.onboarding"))
        return redirect(url_for("recommendations.dashboard"))
    return redirect(url_for("auth.login"))


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("auth.index"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            user.last_login = datetime.utcnow()
            db.session.commit()
            login_user(user)
            if not user.onboarding_complete:
                return redirect(url_for("auth.onboarding"))
            return redirect(url_for("recommendations.dashboard"))
        else:
            flash("Invalid email or password.", "danger")

    return render_template("login.html")


@auth.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("auth.index"))

    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "danger")
            return render_template("register.html")

        if User.query.filter_by(username=username).first():
            flash("Username already taken.", "danger")
            return render_template("register.html")

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("Account created successfully. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth.route("/onboarding")
@login_required
def onboarding():
    if current_user.onboarding_complete:
        return redirect(url_for("recommendations.dashboard"))
    return render_template(
        "onboarding.html", tmdb_api_key=current_app.config["TMDB_API_KEY"]
    )


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
