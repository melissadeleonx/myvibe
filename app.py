import os

from datetime import datetime
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_session import Session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, password_requirements, user_is_logged_in, get_user_info, update_user_profile

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///uniVVV.db")

# # Initialize login manager
# login_manager = LoginManager(app)
# login_manager.login_view = 'login'

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Homepage"""
    user_info = db.execute("SELECT * FROM users WHERE user_id = :user_id", user_id=session["user_id"])

    # Pass the user information to the template
    return render_template("index.html", user_info=user_info[0])


@app.route("/about", methods=["GET"])
def about():
    """About Page"""
    user_info = None  # Fetch user_info if needed
    return render_template("about.html", user_info=user_info)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username or email was submitted
        username_email = request.form.get("username_email")
        password = request.form.get("password")

        if not username_email or not password:
            flash("Captain, we're unable to authenticate. Please check your coordinates (username/email/password).", "error")
            return render_template("login.html"), 400

        # Query database for username or email and non-null password
        rows = db.execute(
            "SELECT * FROM users WHERE (username = :username OR email = :email) AND password IS NOT NULL",
            username=username_email, email=username_email
        )

        # Ensure username or email exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["password"], password
        ):
            flash("Captain, we're unable to authenticate. Please check your coordinates (username/email/password).", "error")
            return render_template("login.html"), 400

        # Remember which user has logged in
        session["user_id"] = rows[0]["user_id"]

        # Redirect user to home page
        flash("Warping into your account... login successful!")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    flash("Logout successful. You've safely exited the wormhole.", "message")
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        birthyear = request.form.get("birthyear")

        # To avoid blank registration form
        if not email or not username or not password or not confirmation or not birthyear:
            flash("\U0001F6A8 Cosmic coordinates incomplete! Please fill in all the required fields.", "error")
            return render_template("register.html"), 400

        # Make sure password is typed again in the second box
        if password != confirmation:
            flash("\U0001F6A8 ALERT! Passwords don't match. Ensure a smooth warp by typing carefully.", "error")
            return render_template("register.html"), 400

        # Additional password restrictions
        if not password_requirements(password):
            flash("\U0001F6A8 Guardians of the Galaxy advise stronger passwords. Enhance your security shield!", "error")
            return render_template("register.html"), 400

        # Implement age restrictions, only above 18
        current_year = datetime.now().year
        age = current_year - int(birthyear)

        if age < 18:
            flash("You must be 18 years or older to register.", "error")
            return render_template("register.html"), 400

        # Check if the email is already registered
        existing_email = db.execute("SELECT * FROM users WHERE email = ?", email)
        if existing_email:
            flash("\U0001F6A8 Email already registered, please use another one.", "error")
            return render_template("register.html"), 400

        existing_user = db.execute("SELECT * FROM users WHERE username = ?", username)
        if existing_user:
            flash("\U0001F6A8 Oops! Looks like someone has already claimed that starship name. Choose another one!", "error")
            return render_template("register.html"), 400

        # Using werkzeug.security, generate a secure way to store the passwords
        hashed_password = generate_password_hash(password)

        # Update our database users table
        user_id = db.execute(
            "INSERT INTO users (username, email, password, birthyear) VALUES (?, ?, ?, ?)",
            username,
            email,
            hashed_password,
            birthyear,
        )

        session["user_id"] = user_id

        flash("Welcome to the uniVVV galaxy! Your journey begins now 🚀.", "message")
        return redirect("/")
    else:
        return render_template("register.html")

@app.route("/allies")
@login_required
def allies():
    """Allies"""
    user_info = db.execute("SELECT * FROM users WHERE user_id = :user_id", user_id=session["user_id"])

    return render_template("allies.html", user_info=user_info[0])

@app.route("/memories")
@login_required
def memories():
    """Memories"""
    user_info = db.execute("SELECT * FROM users WHERE user_id = :user_id", user_id=session["user_id"])

    return render_template("memories.html", user_info=user_info[0])

@app.route("/profile/<username>")
@login_required
def profile(username):
    # Get the user's information from the database based on the username
    user_info = db.execute("SELECT * FROM users WHERE username = :username", username=username)

    # Pass the user information to the template
    return render_template("profile.html", user_info=user_info[0])

@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    """Edit Profile Page"""
    user_id = session["user_id"]
    user_info = get_user_info(user_id)

    if request.method == "POST":
        rank_title = request.form.get("rankTitle")
        username = request.form.get("username")
        birthyear = request.form.get("birthyear")
        species = request.form.get("species")
        planet = request.form.get("planet")
        language = request.form.get("language")
        occupation = request.form.get("occupation")
        favorite_constellation = request.form.get("favorite_constellation")
        interests = request.form.get("interests")
        sex = request.form.get("sex")
        age = request.form.get("age")
        hair_color = request.form.get("hair_color")
        eye_color = request.form.get("eye_color")
        blood_type = request.form.get("blood_type")

        # Update user profile
        update_user_profile(
            user_id,
            rank_title,
            username,
            birthyear,
            species,
            planet,
            language,
            occupation,
            favorite_constellation,
            interests,
            sex,
            age,
            hair_color,
            eye_color,
            blood_type
        )
        return render_template("edit_profile.html", user_info=user_info)

    return render_template("edit_profile.html", user_info=user_info)
