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
    session["users"] = []
    return render_template("register.html")

# when user doesn't have any account yet
@app.route("/sign_up" , methods=["POST" , "GET"])
def sign_up():
    if request.method == "GET":
        return "Please sign up first!"
    if request.method == 'POST':
        if session.get("users") is None:
            session["users"] = []
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        if (db.execute("SELECT * FROM users WHERE username = :username",{"username": username}).rowcount == 0) and (db.execute("SELECT * FROM users WHERE email = :email",{"email": email}).rowcount == 0):
            db.execute("INSERT INTO users (email,password,username) VALUES (:email , :password , :username)" , {
            "email": email, "password":password , "username": username })
            db.commit()
            session["users"].append(username)
            return render_template("signup.html" , Username =session["users"])
        else:
            return "sorry this username or email already exists ,you should peak another username"
# when user already has an account
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

# search engine
@app.route("/search_results", methods=["POST", "GET"])
def search_results():
    if request.method == "GET":
        return "Please sign up first!"
    if request.method == 'POST':
        search = request.form.get("search")
        search = list(search)
        temp = ["%"]
        temp = temp + search
        temp.append("%")
        final_search = ''
        for t in temp:
            final_search += t

        # search for isbn_number
        founded_isbn_numbers = db.execute("SELECT * FROM books5 WHERE isbn_number LIKE (:final_search)",{"final_search":final_search}).fetchall()
        if len(founded_isbn_numbers) == 0:
            founded_isbn_numbers=["not any results"]

        # search for author
        founded_authors =  db.execute("SELECT * FROM books5 WHERE author LIKE (:final_search)",{"final_search":final_search}).fetchall()
        if len(founded_authors) == 0:
            founded_authors=["not any results"]

        # search for title
        founded_titles = db.execute("SELECT * FROM books5 WHERE title LIKE (:final_search)",{"final_search":final_search}).fetchall()
        if len(founded_titles) == 0:
            founded_titles=["not any results"]

        # search for publication_year
        founded_publication_years = db.execute("SELECT * FROM books5 WHERE publication_year LIKE (:final_search)",{"final_search":final_search}).fetchall()
        if len(founded_publication_years) == 0:
            founded_publication_years=["not any results"]
        return render_template("search_results.html",isbn_numbers= founded_isbn_numbers,authors=founded_authors,titles=founded_titles, publication_years=founded_publication_years)
# book page
@app.route("/bookpage/<string:booktext>",methods=["POST","GET"])
def bookpage(booktext):
    book = booktext
    return render_template("bookpage.html", isbn_number=booktext)
