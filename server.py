from flask import Flask,render_template,request,redirect
import sqlite3
app=Flask(__name__)                    
def create_database():                                
   connection=sqlite3.connect("users.db")             #connect to database
   cursor=connection.cursor()                       #store database in some object
   cursor.execute("""CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT,
   Fullname TEXT NOT NULL,
   username TEXT UNIQUE NOT NULL,
   password TEXT NOT NULL)""")        #write query using that object
   connection.commit()              #commit query
   connection.close()             #close connection
@app.route("/")                         
def home():                              
    return render_template("reglogin.html")                           
@app.route("/register",methods=["post"]) 
def register():
   Fullname=request.form["Fullname"]
   username=request.form["username"]
   password=request.form["password"]
   connection=sqlite3.connect("users.db")
   cursor=connection.cursor()  
   cursor.execute("""INSERT INTO users(Fullname,username,password) VALUES(?,?,?)""",(Fullname,username,password))
   connection.commit()
   connection.close()
   return redirect("/login")
@app.route("/login",methods=["get"])
def login_page():                              
   return render_template("login.html")  
@app.route("/login",methods=["post"])
def login():
   username=request.form["username"]
   password=request.form["password"]
   connection=sqlite3.connect("users.db")
   cursor=connection.cursor()
   cursor.execute("""
       SELECT*FROM users
       WHERE username=? AND password=?
       """,(username,password))
   user= cursor.fetchone()
   connection.close()
   if user:
       return "<h2> login successful </h2>"\
       "<p>welcome,"+username+"!</p>"
   else:
        return"<h2>login failed</h2><p>username or password is incorrect</p>"
if __name__=="__main__":
  create_database()
  app.run(debug=True) 