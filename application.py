import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from PIL import Image
import requests

from helpers import apology, login_required, lookup, usd
from hashlib import md5


def avatar(obj, size):
    digest = md5(obj["url"].lower().encode('utf-8')).hexdigest()
    return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
        digest, size)


def img(obj, size):
    digest = md5(str(obj["id"]).lower().encode('utf-8')).hexdigest()
    return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
        digest, size)


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///shop.db")


# Store Categories
CATEGORY = ["Clothing", "Sneakers", "Pets"]


@app.route("/browse/<category>")
def browse(category):
    stores = db.execute("SELECT * FROM stores WHERE lower(category) = ?", category)
    # Add store image
    for store in stores:
        store["logo"] = avatar(store, 800)
    return render_template("browse.html", stores=stores, category=category.capitalize())


@app.route("/")
def index():
    stores = db.execute("SELECT * FROM stores")
    # Add store image
    for store in stores:
        store["logo"] = avatar(store, 800)
    return render_template("index.html", stores=stores)


@app.route("/portal", methods=["GET", "POST"])
@login_required
def portal():
    # Ensure seller account
    if session["usertype"] != "seller":
        return apology("Not a seller account")
    # Pull Store Data
    store = db.execute("SELECT * FROM stores WHERE id = ?", session["user_id"])
    # Frist time setup
    if not store:
        return redirect("/setup")

    # Handle Adding Items
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        price = request.form.get("price").replace(',', '')[1:]
        discount = request.form.get("discount")
        if not discount:
            discount = 0
        quantity = request.form.get("quantity")
        db.execute("INSERT INTO items (storeID, name, description, price, discount, quantity) VALUES (?, ?, ?, ?, ?, ?)",
                   session["user_id"], name, description, price, discount, quantity)
        items = db.execute("SELECT * FROM items WHERE storeID = ?", session["user_id"])
        for item in items:
            item["img"] = img(item, 800)
        flash("Item(s) successfully added")
        return render_template("portal.html", store=store[0], items=items)
    else:
        items = db.execute("SELECT * FROM items WHERE storeID = ?", session["user_id"])
        for item in items:
            item["img"] = img(item, 800)
        return render_template("portal.html", store=store[0], items=items)


@app.route("/product/<productID>")
def product(productID):
    item = db.execute("SELECT * FROM items WHERE id = ?", productID)[0]
    item["img"] = img(item, 800)
    return render_template("product.html", item=item)


@app.route("/buy/<productID>")
@login_required
def buy(productID):
    q = db.execute("SELECT quantity FROM items WHERE id = ?", productID)[0]["quantity"]
    # Check in stock
    if q <= 0:
        return apology("Item Sold Out")
    db.execute("UPDATE items SET quantity = ? WHERE id = ?", q - 1, productID)
    flash("Order successfully placed")
    return redirect("/")


@app.route("/remove/<productID>")
@login_required
def remove(productID):
    # Authorizing removal
    storeID = db.execute("SELECT storeID FROM items WHERE id = ?", productID)
    if storeID[0]["storeID"] != session["user_id"]:
        return apology("Not authorized")
    db.execute("DELETE FROM items WHERE id = ?", productID)
    flash("Item successfully deleted")
    return redirect("/portal")


@app.route("/store/<url>")
def store(url):
    store = db.execute("SELECT * FROM stores WHERE url = ?", url)
    logo = avatar(store[0], 800)
    maincolor = findcolor(logo)
    storeID = store[0]["id"]
    items = db.execute("SELECT * FROM items WHERE storeID = ?", storeID)
    for item in items:
        item["img"] = img(item, 800)
    return render_template("store.html", store=store[0], items=items, logo=logo, maincolor=maincolor)


@app.route("/setup", methods=["GET", "POST"])
@login_required
def setup():
    # Ensure seller account
    if session["usertype"] != "seller":
        return apology("Not a seller account")
    if request.method == "POST":
        name = request.form.get("name")
        url = request.form.get("url")
        category = request.form.get("category")
        phonenumber = request.form.get("phonenumber")
        # Check everything filled
        if (not name) or (not url) or (category not in CATEGORY):
            return apology("Missing info")
        # Check for duplicate URLs
        storeurldup = db.execute("SELECT * FROM stores WHERE url = ?", url)
        if storeurldup:
            return apology("URL is already taken")
        storenamedup = db.execute("SELECT * FROM stores WHERE name = ?", name)
        if storenamedup:
            return apology("Store Name is already taken")
        # Clear old store database
        db.execute("DELETE FROM stores WHERE id = ?", session["user_id"])
        # Insert Store info to database
        db.execute("INSERT INTO stores (id, name, url, category, phonenumber) VALUES (?, ?, ?, ?, ?)",
                   session["user_id"], name, url.lower(), category, phonenumber)
        flash("Store set up successfully")
        return redirect("/portal")
    else:
        return render_template("setup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure email was submitted
        if not request.form.get("email"):
            return apology("must provide e-mail", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for email
        rows = db.execute("SELECT * FROM users WHERE email = ?", request.form.get("email"))

        # Ensure email exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid e-mail and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["usertype"] = rows[0]["usertype"]

        # Redirect user to home page
        flash("Logged in successfully")
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
    flash("Logged out successfully")
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # Error Checking
        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        usertype = request.form.get("usertype")
        rows = db.execute("SELECT * FROM users WHERE email = ?;", email)
        # Ensure the email was submitted
        if not email:
            return apology("must provide email", 400)
        # Ensure the email doesn't exists
        elif len(rows) != 0:
            return apology("email already exists", 400)
        # Ensure password was submitted
        elif not password:
            return apology("must provide password", 400)
        # Ensure confirmation password was submitted
        elif not request.form.get("confirmation"):
            return apology("must provide password confirmation", 400)
        # Ensure passwords match
        elif not password == confirmation:
            return apology("passwords do not match", 400)

        hashed = generate_password_hash(password)
        db.execute("INSERT INTO users (email, hash, usertype) VALUES (?, ?, ?);",
                   email, hashed, usertype)
        # Redirect user to home page
        flash("Successfully Registered!")
        return redirect("/")
    else:
        return render_template("register.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Custom color finder from generated image
def findcolor(url):
    with Image.open(requests.get(url, stream=True).raw) as im:
        rgb_im = im.convert('RGB')
        r, g, b = 255, 255, 255
        i, j = 0, 0
        while (r >= 200 and g >= 200 and b >= 200):
            r, g, b = rgb_im.getpixel((i, j))
            i += 1
            j += 1
    return '#%02x%02x%02x' % (r, g, b)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

