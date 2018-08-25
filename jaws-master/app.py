
import os
import psycopg2
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required

app = Flask(__name__)

conn = psycopg2.connect(database="jaws",user="postgres", password="jessiehou", host="localhost")
cur = conn.cursor()

# Ensure environment variable is set
if not os.getenv("API_KEY"):
    raise RuntimeError("API_KEY not set")

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/pictures", methods=["GET", "POST"])
def pictures():
    if request.method == "POST":

        """Check if they entered a year"""
        if not request.form.get("year"):
            return apology("Please enter a year", 403)

        """Check if they entered which season"""
        if not request.form.get("season"):
            return apology("Please enter a season", 403)

        if ((request.form.get("year") == "2018") & (request.form.get("season") == "Spring")):
            return render_template("getpicture.html", link = "https://drive.google.com/drive/folders/1FmEuX1r0LSMAMoGqhN4Ky36p7O7cekOx")

        else:
            return render_template("comingsoon.html")

    else:
        return render_template("pictures.html")

@app.route("/signups", methods=["GET", "POST"])
def signups():
    if request.method == "POST":
        if not ("user_id" in session.keys()):
            return redirect("/login")
        name = cur.execute("SELECT name FROM users WHERE username == :username", username = session["user_id"])
        """Check if already signed up"""
        rows = cur.execute("Select * FROM Signup WHERE Name == :naame", naame = name[0][0])
        for i in range(len(rows)):
            if request.form.get("wednesday"):
                if rows[i]["day"] == "Wednesday":
                    return apology("Oops! You've already signed up for Wednesday.", 403)
            if request.form.get("saturday"):
                if rows[i]["day"] == "Saturday":
                    return apology("Oops! You've already signed up for Saturday.", 403)
            if request.form.get("sunday"):
                if rows[i]["day"] == "Sunday":
                    return apology("Oops! You've already signed up for Sunday.", 403)
        """Sign Up"""
        if request.form.get("ride"):
            if request.form.get("wednesday"):
                cur.execute("INSERT into Signup (Name, Ride, day) VALUES ( :name, :ride, :day)", name = request.form.get("name"), ride = "True", day = "Wednesday")
            if request.form.get("sunday"):
                cur.execute("INSERT into Signup (Name, Ride, day) VALUES ( :name, :ride, :day)", name = request.form.get("name"), ride = "True", day = "Saturday")
            if request.form.get("saturday"):
                cur.execute("INSERT into Signup (Name, Ride, day) VALUES ( :name, :ride, :day)", name = request.form.get("name"), ride = "True", day = "Sunday")
        else:
            if request.form.get("wednesday"):
                cur.execute("INSERT into Signup (Name, Ride, day) VALUES ( :name, :ride, :day)", name = request.form.get("name"), ride = "False", day = "Wednesday")
            if request.form.get("sunday"):
                cur.execute("INSERT into Signup (Name, Ride, day) VALUES ( :name, :ride, :day)", name = request.form.get("name"), ride = "False", day = "Saturday")
            if request.form.get("saturday"):
                cur.execute("INSERT into Signup (Name, Ride, day) VALUES ( :name, :ride, :day)", name = request.form.get("name"), ride = "False", day = "Sunday")

        return render_template("success.html")

    else:
        return render_template("signups.html")
    
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure name was submitted
        if not request.form.get("name"):
            return apology("must provide a name", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        #Ensure confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must provide confirmation", 403)

        # Ensure confirmation matches password
        if not request.form.get("password") == request.form.get("confirmation"):
            return apology("confirmation and password do not match")
        
        cur.execute("INSERT INTO users (username, password, name) VALUES (%s, %s, %s)", (request.form.get("username"), generate_password_hash(request.form.get("password")), request.form.get("name")))
        conn.commit()

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")
    
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

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
        cur.execute("SELECT * FROM users WHERE username = %(user)s", {"user": request.form.get("username")})
        rows = cur.fetchone()
        
        # Ensure username exists and password is correct
        if rows is None:
            return apology("Invalid username", 403)
        
        elif not check_password_hash(rows[2], request.form.get("password")):
            return apology("Invalid password", 403)
        
        # Remember which user has logged in
        session["user_id"] = rows[0][0]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
    
@app.route("/about", methods=["GET"])
def about():
    return render_template("about.html")

@app.route("/signedup", methods=["GET"])
def signedup():
    if not ("user_id" in session.keys()):
        return redirect("/login")
    #name = cur.execute("SELECT name FROM users WHERE username = :username", username = session["user_id"])
    sdays = cur.execute("SELECT day FROM Signup WHERE Name = %(name)s", {"name" : "Eric"})
    days = []
    if len(sdays) == 0:
        return render_template("signedup.html", days = 0)
    for i in range(len(sdays)):
        days.append(sdays[i]["day"])
    return render_template("signedup.html", days = ", ".join(days))
    
@app.route("/finalcancel", methods=["GET", "POST"])
def finalcancel():
    if request.method == "POST":
        if not request.form.get("side"):
            return apology("Please pick a side", 403)
            # Clear all practices for this user
            cur.execute("SELECT name FROM users WHERE username = %(username)s", {"username" : session["user_id"]})
            name = cur.fetchone()
            cur.execute("DELETE FROM Signup WHERE Name = %(name)s", {"name" : name[0][0]})
            # Re-signup
            if not ("user_id" in session.keys()):
                return redirect("/login")
            if request.form.get("ride"):
                if request.form.get("wednesday"):
                    cur.execute("INSERT into Signup (Name, Ride, day, side) VALUES ( %s, %s, %s, %s)", (name[0][0], "True", "Wednesday", request.form.get("side")))
                    conn.commit()
                if request.form.get("sunday"):
                    cur.execute("INSERT into Signup (Name, Ride, day, side) VALUES ( %s, %s, %s, %s)", (name[0][0], "True", "Saturday", request.form.get("side")))
                    conn.commit()
                if request.form.get("saturday"):
                    cur.execute("INSERT into Signup (Name, Ride, day, side) VALUES ( %s, %s, %s, %s)", (name[0][0], "True", "Sunday", request.form.get("side")))
                    conn.commit()
            else:
                if request.form.get("wednesday"):
                    cur.execute("INSERT into Signup (Name, Ride, day, side) VALUES ( %s, %s, %s, %s)", (name[0][0], "False", "Wednesday", request.form.get("side")))
                    conn.commit()
                if request.form.get("sunday"):
                    cur.execute("INSERT into Signup (Name, Ride, day, side) VALUES ( %s, %s, %s, %s)", (name[0][0], "False", "Saturday", request.form.get("side")))
                    conn.commit()
                if request.form.get("saturday"):
                    cur.execute("INSERT into Signup (Name, Ride, day, side) VALUES ( %s, %s, %s, %s)", (name[0][0], "False", "Sunday", request.form.get("side")))
                    conn.commit()
        return render_template("success.html")
    else:
        if not ("user_id" in session.keys()):
                return redirect("/login")
        cur.execute("SELECT name FROM users WHERE username = %(username)s", {"username": session["user_id"]})
        name = cur.fetchone()
        day = cur.execute("SELECT day FROM Signup WHERE Name = %(name)s", {"name": name[0][0]})        
        ride = cur.execute("SELECT Ride FROM Signup WHERE Name = %(name)s", {"name": name[0][0]})        
        side = cur.execute("SELECT side FROM Signup WHERE Name = %(name)s", {"name": name[0][0]})        
        cur.execute("SELECT day FROM Signup WHERE Name = %(name)s", {"name": name[0][0]})
        row = cur.fetchone()
        rows = []
        while row is not None:
            rows.append(row)
            row = cur.fetchone()
        cur.execute("SELECT * FROM Signup WHERE day = %(day)s", {"day" : "Wednesday"})
        wed = []
        weds = cur.fetchone()
        while weds is not None:
            wed.append(weds)
            weds = cur.fetchone()
        cur.execute("SELECT * FROM Signup WHERE day = %(day)s", {"day" : "Saturday"})
        sat = []
        sats = cur.fetchone()
        while sats is not None:
            sat.append(sats)
            sats = cur.fetchone()
        cur.execute("SELECT * FROM Signup WHERE day = %(day)s", {"day" : "Sunday"})
        sun = []
        suns = cur.fetchone()
        while suns is not None:
            sun.append(suns)
            suns = cur.fetchone()
        wedavailable = len(wed)
        satavailable = len(sat)
        sunavailable = len(sun)
        if len(rows) == 0:
            return render_template("finalcancel.html", a = "", b = "", c = "")
        else:
            if len(rows) == 1:
                if rows[0]["day"] == "Wednesday":
                    return render_template("finalcancel.html", a = "checked", b = "", c = "", day = day, ride = ride, side = side, available = wedavailable)
                if rows[0]["day"] == "Saturday":
                    return render_template("finalcancel.html", a = "", b = "checked", c = "", day = day, ride = ride, side = side, available = satavailable)
                if rows[0]["day"] == "Sunday":
                    return render_template("finalcancel.html", a = "", b = "", c = "checked", day = day, ride = ride, side = side, available = sunavailable)
            if len(rows) == 2:
                if rows[0]["day"] == "Wednesday" and rows[1]["day"] == "Saturday":
                    return render_template("finalcancel.html", a = "checked", b = "checked", c = "", day = day, ride = ride, side = side, available = [wedavailable, satavailable])
                if rows[0]["day"] == "Wednesday" and rows [1]["day"] == "Sunday":
                    return render_template("finalcancel.html", a = "checked", b = "", c = "checked", day = day, ride = ride, side = side, available = [wedavailable, sunavailable])
                if rows[0]["day"] == "Saturday" and rows[1]["day"] == "Sunday":
                    return render_template("finalcancel.html", a = "", b = "checked", c = "checked", day = day, ride = ride, side = side, available = [satavailable, sunavailable])
                if rows[0]["day"] == "Saturday" and rows[1]["day"] == "Wednesday":
                    return render_template("finalcancel.html", a = "checked", b = "checked", c = "", day = day, ride = ride, side = side, available = [satavailable, wedavailable])
                if rows[0]["day"] == "Sunday" and rows[1]["day"] == "Wednesday":
                    return render_template("finalcancel.html", a = "checked", b = "", c = "checked", day = day, ride = ride, side = side, available = [sunavailable, wedavailable])
                if rows[0]["day"] == "Sunday" and rows[1]["day"] == "Saturday":
                    return render_template("finalcancel.html", a = "", b = "checked", c = "checked", day = day, ride = ride, side = side, available = [sunavailable, satavailable])
            if len(rows) == 3:
                if rows[0]["day"] == "Wednesday" and rows[1]["day"] == "Saturday":
                    return render_template("finalcancel.html", a = "checked", b = "checked", c = "", day = day, ride = ride, side = side, available = [wedavailable, satavailable, sunavailable])
                if rows[0]["day"] == "Wednesday" and rows [1]["day"] == "Sunday":
                    return render_template("finalcancel.html", a = "checked", b = "", c = "checked", day = day, ride = ride, side = side, available = [wedavailable, sunavailable, satavailable])
                if rows[0]["day"] == "Saturday" and rows[1]["day"] == "Sunday":
                    return render_template("finalcancel.html", a = "", b = "checked", c = "checked", day = day, ride = ride, side = side, available = [satavailable, sunavailable, wedavailable])
                if rows[0]["day"] == "Saturday" and rows[1]["day"] == "Wednesday":
                    return render_template("finalcancel.html", a = "checked", b = "checked", c = "", day = day, ride = ride, side = side, available = [satavailable, wedavailable, sunavailable])
                if rows[0]["day"] == "Sunday" and rows[1]["day"] == "Wednesday":
                    return render_template("finalcancel.html", a = "checked", b = "", c = "checked", day = day, ride = ride, side = side, available = [sunavailable, wedavailable, satavailable])
                if rows[0]["day"] == "Sunday" and rows[1]["day"] == "Saturday":
                    return render_template("finalcancel.html", a = "", b = "checked", c = "checked", day = day, ride = ride, side = side, available = [sunavailable, satavailable, wedavailable])

            return apology("Oops! Something Went Wrong", 403)
if __name__ == "__main__":
    app.run()