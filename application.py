from flask import render_template, jsonify, request
from flask import Flask, session, redirect
from flask_session import Session

from sqlalchemy import create_engine, or_, and_
from sqlalchemy.orm import scoped_session, sessionmaker
import requests

from models import *

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'postgres://liztyvnfvknrza:2aacdd828389a3218899db7794f58f19860d30fabbfac6e36fe16b2d9e87206f@ec2-107-22-169-45.compute-1.amazonaws.com:5432/d2b89pa095fjbd'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = 'the_secret_key123'
db.init_app(app)

@app.route("/")
def index():
  session['goodread_key'] = 'kHQzDXf3a2fycBlYPlZg'
  if not session.get('username') or not session['username']:
    return render_template("signup.html")
  else:
    return render_template("success.html", user=session['username'])

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/signin", methods=["POST"])
def signin():
    name = request.form.get("name")
    if Users.query.filter(Users.name == name).first():
      return render_template("error.html", message="Username already exists.")
    pwd = request.form.get("pwd")
    sex = request.form.get("sex")
    email = request.form.get("email")

    # Add passenger.
    try:
      user = Users(name=name, password=pwd, sex=sex, email=email)
    except:
      return render_template("error.html", message="Some values are invalid.")
    db.session.add(user)
    db.session.commit()
    session['username'] = user.name
    return render_template("success.html", user=session['username'])

@app.route("/login", methods=["POST"])
def login():
    name = request.form.get("name")
    pwd = request.form.get("pwd")

    client = Users.query.filter(Users.name == name, Users.password == pwd).first()
    if not client:
        return render_template("error.html", message="Username and password do not match any account.")
    session['username'] = client.name
    return render_template("success.html", user=session['username'])

@app.route("/logout")
def logout():
  session['username'] = None
  return render_template("signup.html")


@app.route("/search", methods=["POST"])
def search():
  search = request.form.get("search").lower()
  search_like = "%" + search + "%"
  books = Books.query.filter(or_(Books.isbn.ilike(search_like),
                     Books.title.ilike(search_like),
                     Books.author.ilike(search_like))).all()
  return render_template("books.html", books=books)

@app.route("/write_review/<int:book_id>", methods=["POST"])
def write_review(book_id):
  try:
    user_name = session['username']
    rating = request.form.get("rating")
    review = request.form.get("review")
    book = Books.query.get(book_id)
    if not Reviews.query.filter_by(user_name=user_name, book_id=book.id).first():
      book.add_review(user_name, rating, review)
    else:
      return render_template("error.html", message="You have already entered a review for this book!")
  except:
    return render_template("error.html", message="Unable to add review. Try again later.")
  return redirect("/books/"+book.isbn)

@app.route("/books")
def books():
    books = Books.query.all()
    return render_template("books.html", books=books)


@app.route("/books/<book_id>")
def book(book_id):

    book = Books.query.filter_by(isbn=book_id).first()
    if book is None:
        return render_template("error.html", message="No such book.")

    # Get all reviews.
    reviews = book.reviews
    # get Good Read API values
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": session['goodread_key'], "isbns": book.isbn})
    resj = res.json()['books'][0]
    return render_template("book.html", book=book, reviews=reviews, gr_rating=resj[u'average_rating'], gr_comment=resj[u'reviews_count'])


@app.route("/api/books/<book_id>")
def book_api(book_id):

    book = Books.query.filter_by(isbn=book_id).first()
    if book is None:
        return jsonify({"error": "Invalid book_id"}), 422

    # Get all reviews.
    reviews = book.reviews
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": session['goodread_key'], "isbns": book.isbn})
    resj = res.json()['books'][0]
    return jsonify({
            "title": book.title,
            "author": book.author,
            "year": book.year,
            "rating": resj['average_rating'],
            "nbr_comments": resj['reviews_count']
        })


