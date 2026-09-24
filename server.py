from flask import Flask, request, redirect, render_template, make_response, session, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "employee-management-secret-key"

def get_database_connection():
    connection = sqlite3.connect("users.db")
    connection.row_factory = sqlite3.Row
    return connection

def create_database():
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            department TEXT NOT NULL,
            salary INTEGER NOT NULL,
            joining_date TEXT NOT NULL,
            address TEXT
        )
    """)
    connection.commit()
    connection.close()
    print("Database ready")

def login_required():
    return "user_id" in session

@app.route("/set-theme/<theme>")
def set_theme(theme):
    if theme not in ["light", "dark"]:
        theme = "light"
    previous_page = request.referrer or "/"
    response = make_response(redirect(previous_page))
    response.set_cookie("theme", theme, max_age=60 * 60 * 24 * 365)
    return response

@app.route("/")
def home():
    if not login_required():
        return redirect("/login")
    theme = request.cookies.get("theme", "light")
    return render_template("navbar.html", theme=theme, username=session.get("username"), fullname=session.get("fullname"))

@app.route("/register", methods=["GET", "POST"])
@app.route("/register2", methods=["GET", "POST"])
def register2():
    theme = request.cookies.get("theme", "light")
    if request.method == "POST":
        fullname = request.form.get("fullname","").strip()
        username = request.form.get("username","").strip()
        password = request.form.get("password","")
        if not fullname or not username or not password:
            return render_template("register2.html", theme=theme, error="All fields required.")
        hashed = generate_password_hash(password)
        connection = get_database_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("INSERT INTO users (fullname, username, password) VALUES (?, ?, ?)", (fullname, username, hashed))
            connection.commit()
            connection.close()
            return redirect("/login")
        except sqlite3.IntegrityError:
            connection.close()
            return render_template("register2.html", theme=theme, error="Username already exists.")
    return render_template("register2.html", theme=theme)

@app.route("/login", methods=["GET"])
def login_page():
    if "user_id" in session:
        return redirect("/")
    theme = request.cookies.get("theme", "light")
    return render_template("login.html", theme=theme)

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username","").strip()
    password = request.form.get("password","")
    if not username or not password:
        return render_template("login.html", theme=request.cookies.get("theme","light"), error="Username and password are required.")
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, fullname, username, password FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    connection.close()
    if user is None:
        return render_template("login.html", theme=request.cookies.get("theme","light"), error="Username or password is incorrect.")
    if not check_password_hash(user["password"], password):
        return render_template("login.html", theme=request.cookies.get("theme","light"), error="Username or password is incorrect.")
    session.clear()
    session["user_id"] = user["id"]
    session["username"] = user["username"]
    session["fullname"] = user["fullname"]
    return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/add-employee", methods=["GET"])
def add_employee_page():
    if not login_required():
        return redirect("/login")
    theme = request.cookies.get("theme", "light")
    return render_template("add-employee.html", theme=theme)

@app.route("/add-employee", methods=["POST"])
def add_employee():
    if not login_required():
        return redirect("/login")
    name = request.form.get("name","").strip()
    email = request.form.get("email","").strip()
    phone = request.form.get("phone","").strip()
    department = request.form.get("department","").strip()
    salary = request.form.get("salary","").strip()
    joining_date = request.form.get("joining_date","").strip()
    address = request.form.get("address","").strip()
    if not name or not email or not phone or not department or not salary or not joining_date:
        return "All fields required!"
    try:
        salary = int(salary)
    except ValueError:
        return "Salary must be a number!"
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO employees (name, email, phone, department, salary, joining_date, address) VALUES (?, ?, ?, ?, ?, ?, ?)", (name, email, phone, department, salary, joining_date, address))
    connection.commit()
    connection.close()
    return redirect("/employees")

@app.route("/employees")
def employees():
    if not login_required():
        return redirect("/login")
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM employees ORDER BY id DESC")
    employees_list = cursor.fetchall()
    connection.close()
    theme = request.cookies.get("theme", "light")
    return render_template("employees.html", employees=employees_list, theme=theme)

@app.route("/search")
def search():
    if not login_required():
        return redirect("/login")
    search_text = request.args.get("q","").strip()
    connection = get_database_connection()
    cursor = connection.cursor()
    if search_text:
        search_value = f"%{search_text}%"
        cursor.execute("SELECT * FROM employees WHERE name LIKE ? OR email LIKE ? OR phone LIKE ? OR department LIKE ? ORDER BY id DESC", (search_value, search_value, search_value, search_value))
    else:
        cursor.execute("SELECT * FROM employees ORDER BY id DESC")
    employees_list = cursor.fetchall()
    connection.close()
    theme = request.cookies.get("theme", "light")
    return render_template("employees.html", employees=employees_list, theme=theme, search_text=search_text)

@app.route("/delete-employee/<int:id>")
def delete_employee(id):
    if not login_required():
        return redirect("/login")
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM employees WHERE id = ?", (id,))
    connection.commit()
    connection.close()
    return redirect("/employees")

@app.route("/edit-employee/<int:id>", methods=["GET"])
def edit_employee_page(id):
    if not login_required():
        return redirect("/login")
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM employees WHERE id = ?", (id,))
    employee = cursor.fetchone()
    connection.close()
    if employee is None:
        return "<h2>Employee not found!</h2><a href='/employees'>Back</a>"
    theme = request.cookies.get("theme", "light")
    return render_template("edit-employee.html", employee=employee, theme=theme)

@app.route("/edit-employee/<int:id>", methods=["POST"])
def edit_employee(id):
    if not login_required():
        return redirect("/login")
    name = request.form.get("name","").strip()
    email = request.form.get("email","").strip()
    phone = request.form.get("phone","").strip()
    department = request.form.get("department","").strip()
    salary = request.form.get("salary","").strip()
    joining_date = request.form.get("joining_date","").strip()
    address = request.form.get("address","").strip()
    try:
        salary = int(salary)
    except ValueError:
        return "Salary must be a number!"
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE employees SET name=?, email=?, phone=?, department=?, salary=?, joining_date=?, address=? WHERE id=?", (name, email, phone, department, salary, joining_date, address, id))
    connection.commit()
    connection.close()
    return redirect("/employees")

create_database()
if __name__ == "__main__":
    app.run(debug=True)
