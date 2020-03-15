import os
import re,math,requests
from flask_login import current_user
from flask import Flask, session,render_template,jsonify
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
@app.route("/bookpage/<book>",methods=["POST","GET"])
def bookpage(book):
    # cleaning the book string
    book = book.replace("'","")
    book = book.replace(")","")
    book = book.replace("(","")
    new_book = book.split(",")
    labels = ["ISBN Number","Author","Title","Publication Year"]
    stars = db.execute("SELECT rating FROM reviews WHERE isbn_number= :isbn",{"isbn":new_book[0]}).fetchall()
    if len(stars)==0:
        avg_star = 0
    else:
        stars = str(stars)
        stars = stars.replace("]","")
        stars = stars.replace("[","")
        stars = stars.replace("'","")
        stars = stars.replace(")","")
        stars = stars.replace("(","")
        stars = stars.replace(",","")
        stars = str(stars)
        sum = 0
        for s in stars:
            if s == '"' or s == "'" or s == "''" or s == " ":
                continue
            else:
                print(s)
                sum += int(s)
        avg_star = float("{0:.2f}".format(sum/(len(stars) - math.floor(len(stars)/2) ) ))
    comments = db.execute("SELECT username,comment FROM reviews WHERE isbn_number= :isbn",{"isbn":new_book[0]}).fetchall()
    # using goodreads API key to get information about a book
    res = requests.get("https://www.goodreads.com/book/review_counts.json",params={"key":"WOeVdlmL1oTyhsCdAUw5NA","isbns":"{}".format(new_book[0])})
    data = res.json()
    average_rating_from_goodreades = data["books"][0]['average_rating']
    ratings_the_book_has_received_from_goodreads = data["books"][0]['ratings_count']
    return render_template("bookpage.html",myuser = session["users"][0] , book=new_book, labels=labels,avg_star=avg_star,comments= comments ,myApi= data,average_rating_from_goodreades=average_rating_from_goodreades , ratings_the_book_has_received_from_goodreads=ratings_the_book_has_received_from_goodreads)

@app.route("/bookpage/rating_submited/<isbn_number_of_the_book>",methods=["POST","GET"])
def submit_rating(isbn_number_of_the_book):
    rating_out_of_five = request.form.get("star")
    comment = request.form.get("comment")
    review = db.execute("SELECT comment FROM reviews WHERE isbn_number= :isbn AND username= :username",{"isbn":isbn_number_of_the_book, "username":session["users"][0]}).fetchall()
    if len(review) == 0:
        db.execute("INSERT INTO reviews (isbn_number,username,rating,comment) VALUES (:isbn_number,:username,:rating,:comment)",{"isbn_number":isbn_number_of_the_book,"username":str(session["users"][0]),"rating":str(rating_out_of_five),"comment":comment})
        db.commit()
    else:
        return render_template("submit.html",text="you have already submitted a review for this book")
    return render_template("submit.html",text="your review has submitted")

@app.route("/api/<int:isbn>",methods=["GET"])
def api(isbn):
    book = db.execute("SELECT * FROM books5 WHERE isbn_number= :isbn",{"isbn":str(isbn)}).fetchall()
    if len(book)==0:
        return "Error 404"
    # using goodreads API key to get information about a book
    res = requests.get("https://www.goodreads.com/book/review_counts.json",params={"key":"WOeVdlmL1oTyhsCdAUw5NA","isbns":"{}".format(isbn)})
    data = res.json()
    average_rating_from_goodreades = data["books"][0]['average_rating']
    ratings_the_book_has_received_from_goodreads = data["books"][0]['ratings_count']
    return jsonify({
                    "title": book[0][1],
                    "author": book[0][2],
                    "year": int(book[0][3]),
                    "isbn": book[0][0],
                    "review_count": ratings_the_book_has_received_from_goodreads,
                    "average_score": float(average_rating_from_goodreades)
                    })
