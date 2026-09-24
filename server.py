from flask import Flask, request, redirect, render_template, session
import sqlite3
import re
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "mysecretkey"


def create_database():
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            theme TEXT DEFAULT 'light'
        )
    """)

    # Add theme column if the users table already existed
    try:
        cursor.execute("""
            ALTER TABLE users
            ADD COLUMN theme TEXT DEFAULT 'light'
        """)
    except sqlite3.OperationalError:
        pass

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname TEXT NOT NULL,
            email TEXT NOT NULL,
            department TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


@app.route("/")
def first_page():
    return redirect("/login")


@app.route("/home")
def home():

    if "username" not in session:
        return redirect("/login")

    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT theme
        FROM users
        WHERE username = ?
    """, (session["username"],))

    result = cursor.fetchone()

    connection.close()

    theme = result[0] if result else "light"

    return render_template(
        "home.html",
        theme=theme
    )

@app.route("/register", methods=["GET"])
def register_page():
    return render_template("reglogin.html")


@app.route("/register", methods=["POST"])
def register():

    fullname = request.form["fullname"]
    username = request.form["username"]
    password = request.form["password"]

    # Password validation
    if len(password) < 6 or not re.search("[A-Za-z]", password) or not re.search("[0-9]", password):
        return render_template(
            "reglogin.html",
            error="Password must be at least 6 characters and contain letters and numbers."
        )

    # Hash the password before storing it
    password = generate_password_hash(password)

    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO users (fullname, username, password)
            VALUES (?, ?, ?)
        """, (fullname, username, password))

        connection.commit()

    except sqlite3.IntegrityError:
        connection.close()

        return """
        <h2>Username already exists!</h2>
        <a href="/register">Try Again</a>
        """

    connection.close()

    return redirect("/login")


@app.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():

    username = request.form["username"]
    password = request.form["password"]

    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM users
        WHERE username = ?
    """, (username,))

    user = cursor.fetchone()
    connection.close()

    # Check the entered password with the hashed password
    if user and check_password_hash(user[3], password):

        session["username"] = username

        return redirect("/navbar")

    else:

        return """
        <h2>Login failed!</h2>
        <p>Username or password is incorrect.</p>
        <a href="/login">Try Again</a>
        """


@app.route("/navbar")
def navbar():

    if "username" not in session:
        return redirect("/login")

    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT theme
        FROM users
        WHERE username = ?
    """, (session["username"],))

    result = cursor.fetchone()

    connection.close()

    theme = result[0] if result else "light"

    return render_template(
        "navbar.html",
        username=session["username"],
        theme=theme
    )


@app.route("/save-theme", methods=["POST"])
def save_theme():

    if "username" not in session:
        return redirect("/login")

    data = request.get_json()
    theme = data["theme"]

    if theme not in ["light", "dark"]:
        return "Invalid theme"

    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE users
        SET theme = ?
        WHERE username = ?
    """, (theme, session["username"]))

    connection.commit()
    connection.close()

    return "Theme saved"


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")

@app.route("/employees")
def employees():

    if "username" not in session:
        return redirect("/login")

    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, fullname, email, department, phone
        FROM employees
    """)

    employees = cursor.fetchall()

    cursor.execute("""
        SELECT theme
        FROM users
        WHERE username = ?
    """, (session["username"],))

    result = cursor.fetchone()

    connection.close()

    if result:
        theme = result[0]
    else:
        theme = "light"

    return render_template(
        "employees.html",
        employees=employees,
        theme=theme
    )
@app.route("/dashboard")
def dashboard():

    if "username" not in session:
        return redirect("/login")

    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM employees")
    total_employees = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT department) FROM employees")
    departments = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("""
        SELECT department, COUNT(*)
        FROM employees
        GROUP BY department
    """)

    department_data = cursor.fetchall()

    cursor.execute("""
        SELECT theme
        FROM users
        WHERE username = ?
    """, (session["username"],))

    result = cursor.fetchone()

    connection.close()

    if result:
        theme = result[0]
    else:
        theme = "light"

    return render_template(
        "dashboard.html",
        total_employees=total_employees,
        departments=departments,
        total_users=total_users,
        department_data=department_data,
        theme=theme
    )
@app.route("/delete/<int:id>")
def delete_employee(id):

    if "username" not in session:
        return redirect("/login")

    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM employees WHERE id = ?",
        (id,)
    )

    connection.commit()
    connection.close()

    return redirect("/employees")


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_employee(id):

    if "username" not in session:
        return redirect("/login")

    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()

    if request.method == "POST":

        fullname = request.form["fullname"]
        email = request.form["email"]
        department = request.form["department"]
        phone = request.form["phone"]

        cursor.execute("""
            UPDATE employees
            SET fullname = ?, email = ?, department = ?, phone = ?
            WHERE id = ?
        """, (fullname, email, department, phone, id))

        connection.commit()
        connection.close()

        return redirect("/employees")

    cursor.execute("""
        SELECT id, fullname, email, department, phone
        FROM employees
        WHERE id = ?
    """, (id,))

    employee = cursor.fetchone()

    cursor.execute("""
        SELECT theme
        FROM users
        WHERE username = ?
    """, (session["username"],))

    result = cursor.fetchone()

    connection.close()

    if result:
        theme = result[0]
    else:
        theme = "light"

    return render_template(
        "editemployee.html",
        employee=employee,
        theme=theme
    )

@app.route("/addemployee", methods=["GET", "POST"])
def add_employee():

    if "username" not in session:
        return redirect("/login")

    if request.method == "POST":

        fullname = request.form["fullname"]
        email = request.form["email"]
        department = request.form["department"]
        phone = request.form["phone"]

        connection = sqlite3.connect("users.db")
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO employees
            (fullname, email, department, phone)
            VALUES (?, ?, ?, ?)
        """, (fullname, email, department, phone))

        connection.commit()
        connection.close()

        return redirect("/employees")

    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT theme
        FROM users
        WHERE username = ?
    """, (session["username"],))

    result = cursor.fetchone()

    connection.close()

    if result:
        theme = result[0]
    else:
        theme = "light"

    return render_template(
        "addemployee.html",
        theme=theme
    )

@app.route("/search", methods=["GET", "POST"])
def search():

    if "username" not in session:
        return redirect("/login")

    if request.method == "POST":

        search_name = request.form["search_name"]

        return redirect(
            "/search?search_name=" + search_name
        )

    search_name = request.args.get("search_name", "")

    employees = []

    if search_name:

        connection = sqlite3.connect("users.db")
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, fullname, email, department, phone
            FROM employees
            WHERE fullname LIKE ?
        """, ("%" + search_name + "%",))

        employees = cursor.fetchall()

        connection.close()

    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT theme
        FROM users
        WHERE username = ?
    """, (session["username"],))

    result = cursor.fetchone()

    connection.close()

    if result:
        theme = result[0]
    else:
        theme = "light"

    return render_template(
        "search.html",
        employees=employees,
        search_name=search_name,
        theme=theme
    )

@app.route("/view/<int:id>")
def view_employee(id):

       if "username" not in session:
        return redirect("/login")

       connection = sqlite3.connect("users.db")
       cursor = connection.cursor()

       cursor.execute("""
        SELECT id, fullname, email, department, phone
        FROM employees
        WHERE id = ?
    """, (id,))

       employee = cursor.fetchone()

       cursor.execute("""
        SELECT theme
        FROM users
        WHERE username = ?
    """, (session["username"],))

       result = cursor.fetchone()

       connection.close()

       if result:
        theme = result[0]
       else:
        theme = "light"

       return render_template(
        "viewemployee.html",
        employee=employee,
        theme=theme
    )

if __name__ == "__main__":
    create_database()
    app.run(debug=True)