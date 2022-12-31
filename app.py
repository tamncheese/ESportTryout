import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
import random
import datetime

from helpers import apology, login_required, difference_to_text
# referenced https://stackoverflow.com/questions/17574784/sqlite-current-timestamp-with-milliseconds for recording millisecond in sql db

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
# app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")

# uses code from pset 9 Finance
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# uses code from pset 9 Finance
#uses sql joining and modifying the list of dicts
@app.route("/")
@login_required
def index():
    """Welcome Screen after login"""
    # Show leaderboard
    data = db.execute("SELECT users.username, duration.sequence, duration.tag, duration.motivation, duration.total FROM duration JOIN users ON user_id = users.id ORDER BY total ASC")
    for i in range(len(data)):
        data[i]["rank"] = i + 1
    return render_template("index.html", data = data)

# uses code from pset 9 Finance
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

# uses code from pset 9 Finance
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

# uses code from pset 9 Finance
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("Passwords do not match", 403)
        elif not request.form.get("username"):
            return apology("must provide username", 403)
        elif not request.form.get("password"):
            return apology("must provide password")
        hash = generate_password_hash(request.form.get("password"))
        try:
            checksum = db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", request.form.get("username"), hash)
        except ValueError:
            return apology("username already exists")
        # Remember which user has logged in
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        session["user_id"] = rows[0]["id"]
        db.execute("INSERT INTO duration (user_id) VALUES (?)", session["user_id"])
        return redirect("/")
    else:
        return render_template("register.html")

total_time = 0

@app.route("/sequence", methods=["GET", "POST"])
@login_required
def sequence():
    """Game 1, user presses a sequence of buttons"""
    # SQLite documentation on datetime https://www.sqlite.org/lang_datefunc.html
    # Python documentation on datetime obj https://docs.python.org/3/library/datetime.html#datetime.datetime
    if request.method == "POST":
        db.execute("INSERT INTO times (user_id, game, type) VALUES (?, ?, ?)", session["user_id"], "sequence", "end")
        start = db.execute("SELECT time FROM times WHERE user_id = ? AND game = \"sequence\" AND type = \"start\"", session["user_id"])
        end = db.execute("SELECT time FROM times WHERE user_id = ? AND game = \"sequence\" AND type = \"end\"", session["user_id"])
        start_time_string = start[-1]["time"]
        # how to convert sql string output to datetime obj https://stackoverflow.com/questions/14291636/what-is-the-proper-way-to-convert-between-mysql-datetime-and-python-timestamp
        form = '%Y-%m-%d %H:%M:%S.%f'
        end_time_string = end[-1]["time"]
        start_time = datetime.datetime.strptime(start_time_string, form)
        end_time = datetime.datetime.strptime(end_time_string, form)
        difference = end_time - start_time
        global total_time
        total_time = difference
        sequence_time = difference_to_text(difference)
        db.execute("UPDATE duration SET sequence = ? WHERE user_id = ?", sequence_time, session["user_id"])
        return render_template("tagInstructions.html")
    else:
        # logs start when when the pages loads
        db.execute("INSERT INTO times (user_id, game, type) VALUES (?, ?, ?)", session["user_id"], "sequence", "start")
        # generate a 5x5 square of buttons, each row has a random valid button
        table = []
        num_of_row = 5
        num_of_col = 5
        for i in range(num_of_row):
            row = []
            index = random.randint(0, num_of_col - 1)
            for j in range(5):
                cell = {}
                if j != index:
                    cell["value"] = 0
                    cell["name"] = "incorrect"
                else:
                    cell["value"] = i + 1
                    cell["name"] = "correct"
                row.append(cell)
            table.append(row)
        return render_template("sequence.html", table = table)

@app.route("/sequenceInstructions", methods=["GET", "POST"])
@login_required
def sequenceInstructions():
    if request.method == "POST":
        return redirect("/sequence")
    else:
        return render_template("sequenceInstructions.html")

@app.route("/tagInstructions", methods=["GET", "POST"])
@login_required
def tagInstructions():
    if request.method == "POST":
        return redirect("/tag")
    else:
        return render_template("tagInstructions.html")

@app.route("/tag", methods=["GET", "POST"])
@login_required
def tag():
    if request.method == "POST":
        db.execute("INSERT INTO times (user_id, game, type) VALUES (?, ?, ?)", session["user_id"], "tag", "end")
        start = db.execute("SELECT time FROM times WHERE user_id = ? AND game = \"tag\" AND type = \"start\"", session["user_id"])
        end = db.execute("SELECT time FROM times WHERE user_id = ? AND game = \"tag\" AND type = \"end\"", session["user_id"])
        start_time_string = start[-1]["time"]
        form = '%Y-%m-%d %H:%M:%S.%f'
        end_time_string = end[-1]["time"]
        start_time = datetime.datetime.strptime(start_time_string, form)
        end_time = datetime.datetime.strptime(end_time_string, form)
        difference = end_time - start_time
        global total_time
        total_time += difference
        tag_time = difference_to_text(difference)
        db.execute("UPDATE duration SET tag = ? WHERE user_id = ?", tag_time, session["user_id"])
        return render_template("motivationInstructions.html")
    else:
        # logs start when when the pages loads
        db.execute("INSERT INTO times (user_id, game, type) VALUES (?, ?, ?)", session["user_id"], "tag", "start")
        return render_template("tag.html")

QUOTES =  ["If you think you are too small to make a difference, try sleeping with a mosquito.",
"Talent wins games, but teamwork and intelligence win championships.",
"The nice thing about teamwork is that you always have others on your side.",
"Happiness is not something ready made. It comes from your own actions.",
"When we strive to become better than we are, everything around us becomes better too."]
# Quotes from https://www.inc.com/bill-murphy-jr/366-top-inspirational-quotes-motivational-quotes-for-every-single-day-in-2020.html

@app.route("/motivationInstructions", methods=["GET", "POST"])
@login_required
def motivationInstructions():
    if request.method == "POST":
        return redirect("/motivation")
    else:
        return render_template("motivationInstructions.html")

@app.route("/motivation", methods=["GET", "POST"])
@login_required
def motivation():
    if request.method == "POST":
        db.execute("INSERT INTO times (user_id, game, type) VALUES (?, ?, ?)", session["user_id"], "motivation", "end")
        start = db.execute("SELECT time FROM times WHERE user_id = ? AND game = \"motivation\" AND type = \"start\"", session["user_id"])
        end = db.execute("SELECT time FROM times WHERE user_id = ? AND game = \"motivation\" AND type = \"end\"", session["user_id"])
        start_time_string = start[-1]["time"]
        form = '%Y-%m-%d %H:%M:%S.%f'
        end_time_string = end[-1]["time"]
        start_time = datetime.datetime.strptime(start_time_string, form)
        end_time = datetime.datetime.strptime(end_time_string, form)
        difference = end_time - start_time
        global total_time
        total_time += difference
        motivation_time = difference_to_text(difference)
        user_total = difference_to_text(total_time)
        db.execute("UPDATE duration SET motivation = ? WHERE user_id = ?", motivation_time, session["user_id"])
        db.execute("UPDATE duration SET total = ? WHERE user_id = ?", user_total, session["user_id"])
        return render_template("endScreen.html")
    else:
        # select random quote
        quote = random.randint(0, 4)
        # logs start when when the pages loads
        db.execute("INSERT INTO times (user_id, game, type) VALUES (?, ?, ?)", session["user_id"], "motivation", "start")
        return render_template("motivation.html", quote = quote, answer = QUOTES[quote])

@app.route("/endScreen", methods=["GET", "POST"])
@login_required
def endScreen():
    if request.method == "POST":
        return redirect("/")
    else:
        return render_template("endScreen.html")