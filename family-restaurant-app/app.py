
from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "family-restaurant-demo-key"

MENU = [
    {"id": 1, "name": "Chicken Biryani", "price": 220, "category": "Main Course"},
    {"id": 2, "name": "Veg Biryani", "price": 160, "category": "Main Course"},
    {"id": 3, "name": "Masala Dosa", "price": 80, "category": "Breakfast"},
    {"id": 4, "name": "Paneer Butter Masala", "price": 180, "category": "Main Course"},
    {"id": 5, "name": "French Fries", "price": 100, "category": "Starters"},
    {"id": 6, "name": "Chocolate Ice Cream", "price": 70, "category": "Desserts"}
]


def get_db():
    db = sqlite3.connect("restaurant.db")
    db.row_factory = sqlite3.Row
    return db


def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer TEXT NOT NULL,
                phone TEXT NOT NULL,
                items TEXT NOT NULL,
                total REAL NOT NULL
            )
        """)

        db.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer TEXT NOT NULL,
                phone TEXT NOT NULL,
                booking_date TEXT NOT NULL,
                booking_time TEXT NOT NULL,
                guests INTEGER NOT NULL
            )
        """)


@app.route("/")
def home():
    cart = session.get("cart", {})
    cart_items = []
    total = 0

    for item in MENU:
        quantity = cart.get(str(item["id"]), 0)

        if quantity > 0:
            subtotal = item["price"] * quantity
            cart_items.append({
                **item,
                "quantity": quantity,
                "subtotal": subtotal
            })
            total += subtotal

    return render_template(
        "index.html",
        menu=MENU,
        cart_items=cart_items,
        total=total
    )


@app.route("/add/<int:item_id>", methods=["POST"])
def add_to_cart(item_id):
    if not any(item["id"] == item_id for item in MENU):
        return "Food item not found", 404

    cart = session.get("cart", {})
    key = str(item_id)
    cart[key] = cart.get(key, 0) + 1
    session["cart"] = cart

    flash("Item added to your cart!")
    return redirect(url_for("home"))


@app.route("/remove/<int:item_id>", methods=["POST"])
def remove_from_cart(item_id):
    cart = session.get("cart", {})
    key = str(item_id)

    if key in cart:
        cart[key] -= 1
        if cart[key] <= 0:
            del cart[key]

    session["cart"] = cart
    return redirect(url_for("home"))


@app.route("/checkout", methods=["POST"])
def checkout():
    cart = session.get("cart", {})

    if not cart:
        flash("Please add food to your cart first.")
        return redirect(url_for("home"))

    customer = request.form.get("customer", "").strip()
    phone = request.form.get("phone", "").strip()

    if not customer or not phone:
        flash("Please enter your name and phone number.")
        return redirect(url_for("home"))

    if not phone.isdigit() or len(phone) != 10:
        flash("Enter a valid 10-digit phone number.")
        return redirect(url_for("home"))

    order_items = []
    total = 0

    for item in MENU:
        quantity = cart.get(str(item["id"]), 0)
        if quantity > 0:
            order_items.append(
                f'{item["name"]} x {quantity}'
            )
            total += item["price"] * quantity

    with get_db() as db:
        cursor = db.execute(
            """INSERT INTO orders (customer, phone, items, total)
               VALUES (?, ?, ?, ?)""",
            (customer, phone, ", ".join(order_items), total)
        )
        order_id = cursor.lastrowid

    session["cart"] = {}
    flash(f"Order #{order_id} placed successfully! Total: ₹{total}")
    return redirect(url_for("home"))


@app.route("/book", methods=["POST"])
def book_table():
    customer = request.form.get("customer", "").strip()
    phone = request.form.get("phone", "").strip()
    date = request.form.get("date", "")
    time = request.form.get("time", "")
    guests_text = request.form.get("guests", "")

    try:
        guests = int(guests_text)
    except ValueError:
        guests = 0

    if not all([customer, phone, date, time]):
        flash("Please fill in all table booking details.")
        return redirect(url_for("home"))

    if not phone.isdigit() or len(phone) != 10:
        flash("Enter a valid 10-digit phone number.")
        return redirect(url_for("home"))

    if guests < 1 or guests > 20:
        flash("Guest count must be between 1 and 20.")
        return redirect(url_for("home"))

    from datetime import date as date_type
    if date < date_type.today().isoformat():
        flash("Please select today or a future date.")
        return redirect(url_for("home"))

    with get_db() as db:
        cursor = db.execute(
            """INSERT INTO bookings
               (customer, phone, booking_date, booking_time, guests)
               VALUES (?, ?, ?, ?, ?)""",
            (customer, phone, date, time, guests)
        )
        booking_id = cursor.lastrowid

    flash(f"Table booking request #{booking_id} saved successfully!")
    return redirect(url_for("home"))

from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "family-restaurant-demo-key"

MENU = [
    {"id": 1, "name": "Chicken Biryani", "price": 220, "category": "Main Course"},
    {"id": 2, "name": "Veg Biryani", "price": 160, "category": "Main Course"},
    {"id": 3, "name": "Masala Dosa", "price": 80, "category": "Breakfast"},
    {"id": 4, "name": "Paneer Butter Masala", "price": 180, "category": "Main Course"},
    {"id": 5, "name": "French Fries", "price": 100, "category": "Starters"},
    {"id": 6, "name": "Chocolate Ice Cream", "price": 70, "category": "Desserts"}
]


def get_db():
    db = sqlite3.connect("restaurant.db")
    db.row_factory = sqlite3.Row
    return db


def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer TEXT NOT NULL,
                phone TEXT NOT NULL,
                items TEXT NOT NULL,
                total REAL NOT NULL
            )
        """)

        db.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer TEXT NOT NULL,
                phone TEXT NOT NULL,
                booking_date TEXT NOT NULL,
                booking_time TEXT NOT NULL,
                guests INTEGER NOT NULL
            )
        """)


@app.route("/")
def home():
    cart = session.get("cart", {})
    cart_items = []
    total = 0

    for item in MENU:
        quantity = cart.get(str(item["id"]), 0)

        if quantity > 0:
            subtotal = item["price"] * quantity
            cart_items.append({
                **item,
                "quantity": quantity,
                "subtotal": subtotal
            })
            total += subtotal

    return render_template(
        "index.html",
        menu=MENU,
        cart_items=cart_items,
        total=total
    )


@app.route("/add/<int:item_id>", methods=["POST"])
def add_to_cart(item_id):
    if not any(item["id"] == item_id for item in MENU):
        return "Food item not found", 404

    cart = session.get("cart", {})
    key = str(item_id)
    cart[key] = cart.get(key, 0) + 1
    session["cart"] = cart

    flash("Item added to your cart!")
    return redirect(url_for("home"))


@app.route("/remove/<int:item_id>", methods=["POST"])
def remove_from_cart(item_id):
    cart = session.get("cart", {})
    key = str(item_id)

    if key in cart:
        cart[key] -= 1
        if cart[key] <= 0:
            del cart[key]

    session["cart"] = cart
    return redirect(url_for("home"))


@app.route("/checkout", methods=["POST"])
def checkout():
    cart = session.get("cart", {})

    if not cart:
        flash("Please add food to your cart first.")
        return redirect(url_for("home"))

    customer = request.form.get("customer", "").strip()
    phone = request.form.get("phone", "").strip()

    if not customer or not phone:
        flash("Please enter your name and phone number.")
        return redirect(url_for("home"))

    if not phone.isdigit() or len(phone) != 10:
        flash("Enter a valid 10-digit phone number.")
        return redirect(url_for("home"))

    order_items = []
    total = 0

    for item in MENU:
        quantity = cart.get(str(item["id"]), 0)
        if quantity > 0:
            order_items.append(
                f'{item["name"]} x {quantity}'
            )
            total += item["price"] * quantity

    with get_db() as db:
        cursor = db.execute(
            """INSERT INTO orders (customer, phone, items, total)
               VALUES (?, ?, ?, ?)""",
            (customer, phone, ", ".join(order_items), total)
        )
        order_id = cursor.lastrowid

    session["cart"] = {}
    flash(f"Order #{order_id} placed successfully! Total: ₹{total}")
    return redirect(url_for("home"))


@app.route("/book", methods=["POST"])
def book_table():
    customer = request.form.get("customer", "").strip()
    phone = request.form.get("phone", "").strip()
    date = request.form.get("date", "")
    time = request.form.get("time", "")
    guests_text = request.form.get("guests", "")

    try:
        guests = int(guests_text)
    except ValueError:
        guests = 0

    if not all([customer, phone, date, time]):
        flash("Please fill in all table booking details.")
        return redirect(url_for("home"))

    if not phone.isdigit() or len(phone) != 10:
        flash("Enter a valid 10-digit phone number.")
        return redirect(url_for("home"))

    if guests < 1 or guests > 20:
        flash("Guest count must be between 1 and 20.")
        return redirect(url_for("home"))

    from datetime import date as date_type
    if date < date_type.today().isoformat():
        flash("Please select today or a future date.")
        return redirect(url_for("home"))

    with get_db() as db:
        cursor = db.execute(
            """INSERT INTO bookings
               (customer, phone, booking_date, booking_time, guests)
               VALUES (?, ?, ?, ?, ?)""",
            (customer, phone, date, time, guests)
        )
        booking_id = cursor.lastrowid

    flash(f"Table booking request #{booking_id} saved successfully!")
    return redirect(url_for("home"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
