import os

from flask import Flask, session,render_template
from flask import Flask, session,render_template,request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("register.html")
    # return "helooooo"

@app.route("/sign_up" , methods=["POST" , "GET"])
def sign_up():
    if request.method == "GET":
        return "Please sign up first!"
    if request.method == 'POST':
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        if (db.execute("SELECT * FROM users WHERE username = :username",{"username": username}).rowcount == 0) and (db.execute("SELECT * FROM users WHERE email = :email",{"email": email}).rowcount == 0):
            db.execute("INSERT INTO users (email,password,username) VALUES (:email , :password , :username)" , {
            "email": email, "password":password , "username": username })
            db.commit()
            return render_template("signup.html" , Username =session["users"])
        else:
            return "sorry this username already exists ,you should peak another username"

@app.route("/log_in", methods=["POST" , "GET"])
def log_in():
    if request.method == "GET":
        return "Please sign up first!"
    if request.method == 'POST':
        if session.get("users") is None:
            session["users"] = []
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        # check if username and password are match
        if (db.execute("SELECT password FROM users WHERE username = :username and password = :password" ,{"username":username, "password":password}).rowcount == 1):
            session["users"].append(username)
            return render_template("login.html" , users=session["users"])
        else:
            return render_template("error.html")
