from flask import Flask, request, redirect, render_template
import sqlite3

app = Flask(__name__)


# Create database and tables
def create_database():
 
   connection = sqlite3.connect("users.db")
   cursor = connection.cursor()

  # Users table - for Register/Login
   cursor.execute("""
      CREATE TABLE IF NOT EXISTS users (
         id INTEGER PRIMARY KEY AUTOINCREMENT,
         fullname TEXT NOT NULL,
         username TEXT UNIQUE NOT NULL,
         password TEXT NOT NULL
      )
  """)

  # Employees table
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


# First page
@app.route("/")
def navbar():
 
   return render_template("navbar.html")

# Home page
@app.route("/home")
def home():
 
   return render_template("home.html")

# Register page
@app.route("/register", methods=["GET"])
def register_page():
 
   return render_template("reglogin.html")

# Register user
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


# Login page
@app.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")


# Login user
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

 
# Employees page
@app.route("/employees")
def employees():
 
     connection = sqlite3.connect("users.db")
     cursor = connection.cursor()

     cursor.execute("""
        SELECT id, fullname, email, department, phone
        FROM employees
     """)

     employees = cursor.fetchall()

     connection.close()

     return render_template("employees.html", employees=employees)


#Delete Employee
@app.route("/delete/<int:id>")
def delete_employee(id):

    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()
    
    cursor.execute(
            "DELETE FROM EMPLOYEES WHERE id = ?",
            (id,)
         )
    connection.commit()
    connection.close()

    return redirect("/employees")


#Edit Employee
@app.route("/edit/<int:id>", methods=["GET","POST"])
def edit_employee(id):

    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()

    if request.method == "POST":

      fullname = request.form["fullname"]
      email= request.form["email"]
      department = request.form["department"]
      phone = request.form["phone"]
   
      cursor.execute("""
            UPDATE employees
            SET fullname=?, email=? ,department=? ,phone=?
            WHERE id=?
         """,(fullname,email,department,phone,id))
      connection.commit()
      connection.close()

      return redirect("/employees")

    cursor.execute("""
                  SELECT id,fullname,email,department,phone
                  FROM employees
                  WHERE id=?
                 """,(id,))

    employee=cursor.fetchone()

    connection.close()
      
    return render_template("editemployee.html",employee=employee)
    
    
# Add Employee
@app.route("/addemployee", methods=["GET", "POST"])
def addemployee():
 
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

      return render_template("addemployee.html")


# Search Employee
@app.route("/search", methods=["GET", "POST"])
def search():
 
      employees = []
      search_name = ""

      if request.method == "POST":

          search_name = request.form["search_name"]

          connection = sqlite3.connect("users.db")
          cursor = connection.cursor()

          cursor.execute("""
               SELECT id, fullname, email, department, phone
               FROM employees
               WHERE fullname LIKE ?
          """, ("%" + search_name + "%",))

          employees = cursor.fetchall()

          connection.close()

      return render_template(
         "search.html",
          employees=employees,
          search_name=search_name
      )


# Run Flask
if __name__ == "__main__":
 
      create_database()

      app.run(debug=True)
      