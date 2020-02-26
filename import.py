import os

import csv
from flask import Flask, session,render_template,request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

count =1
f = open("books.csv")
reader = csv.reader(f)
for isbn_number , title , author , publication_year in reader:
    db.execute("INSERT INTO books5(isbn_number,title,author,publication_year) VALUES (:isbn_number,:title,:author,:publication_year)" ,
                    {"isbn_number": isbn_number , "title": title , "author": author , "publication_year":publication_year})
    print("{}Added {} and {} and {} and {}".format(count,isbn_number,title,author,publication_year))
    count += 1
db.commit()
