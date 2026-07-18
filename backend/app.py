from flask import Flask, render_template, request, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

app = Flask(__name__)
app.secret_key = "foodexpress_secret_key"

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="san",
    database="foodexpress"
)


# ---------------- HOME ---------------- #

@app.route('/')
def home():

    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM food_items")

    foods = cursor.fetchall()

    if 'user_name' in session:
        username = session['user_name']
    else:
        username = None

    return render_template(
        "index.html",
        foods=foods,
        username=username
    )


# ---------------- REGISTER ---------------- #

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == "POST":

        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        cursor = db.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM users WHERE email=%s",
            (email,)
        )

        existing = cursor.fetchone()

        if existing:
            return "Email already exists!"

        hashed_password = generate_password_hash(password)

        cursor = db.cursor()

        cursor.execute(
            """
            INSERT INTO users(name,email,password)
            VALUES(%s,%s,%s)
            """,
            (
                name,
                email,
                hashed_password
            )
        )

        db.commit()

        return redirect('/login')

    return render_template("register.html")


# ---------------- LOGIN ---------------- #

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == "POST":

        email = request.form['email']
        password = request.form['password']

        cursor = db.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM users WHERE email=%s",
            (email,)
        )

        user = cursor.fetchone()

        if user:

            if check_password_hash(
                user['password'],
                password
            ):

                session['user_id'] = user['id']
                session['user_name'] = user['name']

                return redirect('/')

        return "Invalid Email or Password!"

    return render_template("login.html")


# ---------------- LOGOUT ---------------- #

@app.route('/logout')
def logout():

    session.clear()

    return redirect('/')
    # ---------------- ADD TO CART ---------------- #

@app.route('/add_to_cart/<int:food_id>')
def add_to_cart(food_id):

    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']

    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM cart WHERE user_id=%s AND food_id=%s",
        (user_id, food_id)
    )

    item = cursor.fetchone()

    if item:

        cursor = db.cursor()

        cursor.execute(
            """
            UPDATE cart
            SET quantity = quantity + 1
            WHERE id=%s
            """,
            (item['id'],)
        )

    else:

        cursor = db.cursor()

        cursor.execute(
            """
            INSERT INTO cart(user_id, food_id, quantity)
            VALUES(%s,%s,%s)
            """,
            (user_id, food_id, 1)
        )

    db.commit()

    return redirect('/cart')


# ---------------- CART ---------------- #

@app.route('/cart')
def cart():

    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']

    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            cart.id,
            cart.food_id,
            food_items.name,
            food_items.price,
            cart.quantity
        FROM cart
        JOIN food_items
        ON cart.food_id = food_items.id
        WHERE cart.user_id=%s
    """, (user_id,))

    cart_items = cursor.fetchall()

    total = 0

    for item in cart_items:
        total += item['price'] * item['quantity']

    return render_template(
        "cart.html",
        cart_items=cart_items,
        total=total
    )


# ---------------- INCREASE QUANTITY ---------------- #

@app.route('/increase_quantity/<int:cart_id>')
def increase_quantity(cart_id):

    cursor = db.cursor()

    cursor.execute(
        """
        UPDATE cart
        SET quantity = quantity + 1
        WHERE id=%s
        """,
        (cart_id,)
    )

    db.commit()

    return redirect('/cart')


# ---------------- DECREASE QUANTITY ---------------- #

@app.route('/decrease_quantity/<int:cart_id>')
def decrease_quantity(cart_id):

    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT quantity FROM cart WHERE id=%s",
        (cart_id,)
    )

    item = cursor.fetchone()

    if item:

        if item['quantity'] > 1:

            cursor = db.cursor()

            cursor.execute(
                """
                UPDATE cart
                SET quantity = quantity - 1
                WHERE id=%s
                """,
                (cart_id,)
            )

        else:

            cursor = db.cursor()

            cursor.execute(
                "DELETE FROM cart WHERE id=%s",
                (cart_id,)
            )

        db.commit()

    return redirect('/cart')


# ---------------- REMOVE ITEM ---------------- #

@app.route('/remove_item/<int:cart_id>')
def remove_item(cart_id):

    cursor = db.cursor()

    cursor.execute(
        "DELETE FROM cart WHERE id=%s",
        (cart_id,)
    )

    db.commit()

    return redirect('/cart')
    # ---------------- PLACE ORDER ---------------- #

@app.route('/place_order')
def place_order():

    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']

    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            cart.food_id,
            food_items.price,
            cart.quantity
        FROM cart
        JOIN food_items
        ON cart.food_id = food_items.id
        WHERE cart.user_id=%s
    """, (user_id,))

    cart_items = cursor.fetchall()

    if len(cart_items) == 0:
        return "Your cart is empty!"

    total = 0

    for item in cart_items:
        total += item['price'] * item['quantity']

    cursor = db.cursor()

    cursor.execute(
        """
        INSERT INTO orders(user_id,total_price)
        VALUES(%s,%s)
        """,
        (user_id, total)
    )

    db.commit()

    order_id = cursor.lastrowid

    for item in cart_items:

        cursor.execute(
            """
            INSERT INTO order_items
            (order_id,food_id,quantity,price)
            VALUES(%s,%s,%s,%s)
            """,
            (
                order_id,
                item['food_id'],
                item['quantity'],
                item['price']
            )
        )

    db.commit()

    cursor.execute(
        "DELETE FROM cart WHERE user_id=%s",
        (user_id,)
    )

    db.commit()

    return redirect('/orders')


# ---------------- MY ORDERS ---------------- #

@app.route('/orders')
def orders():

    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']

    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM orders
        WHERE user_id=%s
        ORDER BY order_date DESC
    """, (user_id,))

    orders = cursor.fetchall()

    return render_template(
        "orders.html",
        orders=orders
    )


# ---------------- ORDER DETAILS ---------------- #

@app.route('/order_details/<int:order_id>')
def order_details(order_id):

    if 'user_id' not in session:
        return redirect('/login')

    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            food_items.name,
            order_items.quantity,
            order_items.price
        FROM order_items
        JOIN food_items
        ON order_items.food_id = food_items.id
        WHERE order_items.order_id=%s
    """, (order_id,))

    items = cursor.fetchall()

    return render_template(
        "order_details.html",
        items=items
    )
    # ---------------- ADMIN PANEL ---------------- #

@app.route('/admin')
def admin():

    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM food_items
        ORDER BY id DESC
    """)

    foods = cursor.fetchall()

    return render_template(
        "admin.html",
        foods=foods
    )


# ---------------- ADD FOOD ---------------- #

@app.route('/add_food', methods=['GET', 'POST'])
def add_food():

    if request.method == "POST":

        name = request.form['name']
        price = request.form['price']

        cursor = db.cursor()

        cursor.execute(
            """
            INSERT INTO food_items(name,price)
            VALUES(%s,%s)
            """,
            (name, price)
        )

        db.commit()

        return redirect('/admin')

    return render_template("add_food.html")


# ---------------- EDIT FOOD ---------------- #

@app.route('/edit_food/<int:food_id>', methods=['GET', 'POST'])
def edit_food(food_id):

    cursor = db.cursor(dictionary=True)

    if request.method == "POST":

        name = request.form['name']
        price = request.form['price']

        cursor = db.cursor()

        cursor.execute(
            """
            UPDATE food_items
            SET name=%s,
                price=%s
            WHERE id=%s
            """,
            (
                name,
                price,
                food_id
            )
        )

        db.commit()

        return redirect('/admin')

    cursor.execute(
        "SELECT * FROM food_items WHERE id=%s",
        (food_id,)
    )

    food = cursor.fetchone()

    return render_template(
        "edit_food.html",
        food=food
    )


# ---------------- DELETE FOOD ---------------- #

@app.route('/delete_food/<int:food_id>')
def delete_food(food_id):

    cursor = db.cursor()

    cursor.execute(
        "DELETE FROM food_items WHERE id=%s",
        (food_id,)
    )

    db.commit()

    return redirect('/admin')
    # ---------------- RUN APP ---------------- #

if __name__ == "__main__":
    app.run(debug=True)