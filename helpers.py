import csv
import datetime
import pytz
import requests
import subprocess
import urllib
import uuid
import re

from cs50 import SQL
from flask import redirect, render_template, session, flash
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

def user_is_logged_in():
    """Check if the user is logged in."""
    return session.get("user_id") is not None

def password_requirements(password):
    pattern = re.compile(
        r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$"
    )
    return bool(re.match(pattern, password))

def get_user_info(user_id):
    """Lookup user information by user_id."""
    db = SQL("sqlite:///uniVVV.db")
    user_info = db.execute("SELECT * FROM users WHERE user_id = :user_id", user_id=user_id)

    # Check if user_info is not empty
    if user_info:
        return user_info[0]
    else:
        return None

def update_user_profile(user_id, rank_title, username, birthyear, species, planet, language, occupation,
                         favorite_constellation, interests, sex, age, hair_color, eye_color, blood_type):
    """Update user profile in the database."""
    db = SQL("sqlite:///uniVVV.db")
    result = db.execute(
        """
        UPDATE users SET
        rank_title = :rank_title,
        username = :username,
        birthyear = :birthyear,
        species = :species,
        planet = :planet,
        language = :language,
        occupation = :occupation,
        favorite_constellation = :favorite_constellation,
        interests = :interests,
        sex = :sex,
        age = :age,
        hair_color = :hair_color,
        eye_color = :eye_color,
        blood_type = :blood_type
        WHERE user_id = :user_id
        """,
        user_id=user_id,
        rank_title=rank_title or None,
        username=username or None,
        birthyear=birthyear or None,
        species=species or None,
        planet=planet or None,
        language=language or None,
        occupation=occupation or None,
        favorite_constellation=favorite_constellation or None,
        interests=interests or None,
        sex=sex or None,
        age=age or None,
        hair_color=hair_color or None,
        eye_color=eye_color or None,
        blood_type=blood_type or None
    )

    if result:
        flash("Profile successfully updated!", "message")
    else:
        flash("Failed to update profile. Please try again.", "danger")
