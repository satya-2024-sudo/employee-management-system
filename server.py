from flask import Flask, request, redirect, render_template
import sqlite3

app = Flask(__name__)


# -----------------------------------
# Create Database and Table
# -----------------------------------
def get_database_connection():
    connection=sqlite3.connect("users.db")
    connection.row_factory=sqlite3.Row
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
    #EMPLOYEE TABLE
    cursor.execute("""
       CREATE TABLE IF NOT EXISTS employees(
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


# -----------------------------------
# Home Page - Navbar
# -----------------------------------

@app.route("/")
def home():

    return render_template("navbar.html")
   #return "server_running"


# -----------------------------------
# Registration Page - GET
# -----------------------------------

@app.route("/register", methods=["GET"])
def register_page():

    return render_template("register2.html")


# -----------------------------------
# Registration Path - POST
# -----------------------------------

@app.route("/register", methods=["POST"])
def register():

    fullname = request.form["fullname"]
    username = request.form["username"]
    password = request.form["password"]

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


# -----------------------------------
# Login Page - GET
# -----------------------------------

@app.route("/login", methods=["GET"])
def login_page():

    return render_template("login.html")


# -----------------------------------
# Login Path - POST
# -----------------------------------

@app.route("/login", methods=["POST"])
def login():

    username = request.form["username"]
    password = request.form["password"]

    connection = sqlite3.connect("users.db")

    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM users
        WHERE username = ? AND password = ?
    """, (username, password))

    user = cursor.fetchone()

    connection.close()

    if user:

        return """
        <h2>Login successful!</h2>
        <p>Welcome, """ + username + """!</p>
        <a href="/">Go to Home</a>
        """

    else:

        return """
        <h2>Login failed!</h2>
        <p>Username or password is incorrect.</p>
        <a href="/login">Try Again</a>
        """


#----------------------------------------
# add employee get
# --------------------------------------

@app.route('/add-employee',methods=["GET"])  
def add_employee_page():
    return render_template("add-employee.html")
#________________________________________
# add employee post
# ________________________________________ 
@app.route('/add-employee',methods=["POST"])
def add_employee():
    name=request.form["name"]
    email=request.form["email"]
    phone=request.form["phone"]
    department=request.form["department"]
    salary=request.form["salary"]
    joiningdate=request.form["joining_date"]
    address=request.form["address"]  

    print("=================================")
    print("ADDING EMPLOYEE")
    print("Name:",name)
    print("Email:",email)
    print("Phone:",phone)
    print("Department",department)
    print("Salary",salary)
    print("Joining Date",joiningdate)
    print("address:",address)
    print("===========================")
    connection=sqlite3.connect("users.db")
    cursor=connection.cursor() 

    try: 

      cursor.execute("""
       INSERT INTO employees (name,email,phone,department,salary,joining_date,address)
        VALUES(?,?,?,?,?,?,?)""",(name,email,phone,department,salary,joiningdate,address
      ) )
      connection.commit()
      print("employee inserted successfully!")
      print("New Employee ID:",cursor.lastrowid)
    except sqlite3.Error as error:
        connection.rollback()
        print("Database Error:",error)
        connection.close()
        return f"""
        <h2>Error adding employee</h2>
        <p>{error}</P>
        <br>
        <a href="/add-employee">
          Go Back
         </a>
         """
    connection.close() 
    
    return redirect("/employees")
"""
      <h2>Employee added successfully!</h2>
      <br>
      <a href="/add-employee">
      Add Another Employee
      </a>
      <br></br>
      <a href="/"
      go to Home
      </a>
      """
#________________________________________
# employees route
#________________________________________
@app.route("/employees")
def employee():
    connection = sqlite3.connect("users.db")
    connection.row_factory=sqlite3.Row
    cursor=connection.cursor()
    cursor.execute("""
    SELECT * FROM employees ORDER BY id DESC
    """)
    employees=cursor.fetchall()
    connection.close()
    return render_template(
        "employees.html",
        employees=employees

    )
#______________________________
# delete employee
#______________________________
@app.route("/delete-employee/<int:id>")
def delete_employee(id):
    connection = sqlite3.connect("users.db")
    cursor=connection.cursor()
    cursor.execute("""
    DELETE FROM employees
    WHERE id=?
    """,(id,))
    connection.commit()
    connection.close()
    return redirect("/employees")
#_______________________________________
#edit employee-display form
#________________________________________

@app.route("/edit-employee/<int:id>")
def edit_employee_page(id):
    connection=get_database_connection()
    cursor=connection.cursor()
    cursor.execute("""
    SELECT * FROM employees
    WHERE id=?
    """,(id,))
    employee=cursor.fetchone()
    connection.close()
    if employee is None:
        return """
        <h2>employee not found</h2><br>
        <a href="/employees">back to employees</a>
        """
    return render_template(
        "edit-employee.html",
        employee=employee
    )

#__________________________________________
#edit employee-update
#__________________________________________
@app.route("/edit-employee/<int:id>",methods=["POST"])
def edit_employee(id):

    name = request.form["name"]
    email=request.form["email"]
    phone=request.form["phone"]
    department=request.form["department"]
    salary=request.form["salary"]
    joining_date=request.form["joining_date"]
    address=request.form["address"]
    connection=sqlite3.connect("users.db")
    cursor=connection.cursor()
    cursor.execute("""
    UPDATE employees
    SET
    
       name=?,
       email=?,
       phone=?,
       department=?,
       salary=?,
       joining_date=?,
       address=?
     WHERE   id =?  
  """,(
          name,
          email,
          phone,
          department,
          salary,
          joining_date,
          address,
          id

      ) )
    connection.commit()
    connection.close()
    return redirect("/employees")
#-----------------------------------
# Start Server
# -----------------------------------

if __name__ == "__main__":

    create_database()

    app.run(debug=True)

    



