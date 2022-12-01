import os
import requests
from flask import Flask, session, render_template, request, redirect, jsonify, flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from helpers import login_required

from werkzeug.security import check_password_hash, generate_password_hash

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
@login_required
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
 
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("error.html", message="must provide username")


        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("error.html", message="must provide password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                            {"username": request.form.get("username")}).fetchone()

        # Ensure username exists and password is correct
        if rows == None or not check_password_hash(rows[2], request.form.get("password")):
            return render_template("error.html", message="invalid username and/or password")
 
        # Remember which user has logged in
        session["user_id"] = rows[0]

        # Redirect user to home page
        return redirect("/")

    else:
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Log user in"""
 
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        if not request.form.get("username"):
            return render_template("error.html", message="must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("error.html", message="must provide password")
        
        elif not request.form.get("confirmation"):
            return render_template("error.html", message="must confirm password")
        
        elif not request.form.get("password") == request.form.get("confirmation"):
            return render_template("error.html", message="passwords do not match")
        
        # Query database for username
        usernameCheck = db.execute("SELECT * FROM users WHERE username = :username",
                        {"username": request.form.get("username")}).fetchone()

        # Ensure username exists and password is correct
        if usernameCheck:
            return render_template("error.html", message="username not available")

        hashedPassword = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8)

        db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
                            {"username": request.form.get("username"), "password": hashedPassword})
        
        db.commit()
        
        return render_template("error.html", message="Account created login to start using it!")

    else:
        return render_template("register.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/search", methods=["GET"])
@login_required
def search():
       
    if not request.args.get("book"):
        return render_template("error.html", message="must provide a Book, Author, year or isbn")

    book = request.args.get("book")
    book = "%" + request.args.get("book") + "%"
    book = book.title()

    rows = db.execute("SELECT isbn, title, author, year FROM books WHERE \
                    isbn LIKE :book OR \
                    title LIKE :book OR \
                    author LIKE :book",
                    {"book": book})

    if not rows:
        return render_template("error.html", message="Sorry! Book not found")

    books = rows.fetchall()

    return render_template("search.html", books=books)

@app.route("/book/<isbn>", methods=["GET", "POST"])
@login_required
def book(isbn):

    if request.method == "POST":
        
        if not request.form.get("rating"):
            return render_template("error.html", message="must provide rating")

        if not request.form.get("comment"):
            return render_template("error.html", message="must provide comment")
            return redirect("/book/" + isbn)

        bookId = db.execute("SELECT id FROM books WHERE isbn = :isbn",
                        {"isbn": isbn}).fetchone()

        user = session["user_id"]
        bookId = bookId[0]

        checkReview = db.execute("SELECT * FROM reviews WHERE user_id = :user_id AND book_id = :book_id",
                                     {"user_id": user, "book_id": bookId})

        if checkReview.rowcount == 1:           
            flash('You already submitted a review for this book', 'warning')
            return redirect("/book/" + isbn)

        db.execute("INSERT INTO reviews (user_id, book_id, comment, rating) VALUES (:user_id, :book_id, :comment, :rating)",
                    {"user_id": user, 
                    "book_id": bookId, 
                    "comment": request.form.get("comment"), 
                    "rating": int(request.form.get("rating"))})

        db.commit()

        flash('Review submitted!', 'info')

        return redirect("/book/" + isbn)


    else:     
        book = db.execute("SELECT isbn, title, author, year FROM books WHERE isbn = :isbn",
                            {"isbn": isbn}).fetchall()
        
        if book is None:
            return render_template("error.html", message="Sorry! Book not found")

        key = os.getenv("GOODREADS_KEY")
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": key, "isbns": isbn})
        
        response = res.json()
        response = response['books'][0]

        book.append(response)

        """ Users reviews """

        book_id = db.execute("SELECT id FROM books WHERE isbn = :isbn",
                        {"isbn": isbn}).fetchone()
        book_id = book_id[0]

        reviews = db.execute("SELECT users.username, comment, rating FROM users INNER JOIN reviews ON users.id = reviews.user_id \
                             WHERE book_id = :book_id",
                            {"book_id": book_id}).fetchall()

        return render_template("book.html", book=book, reviews=reviews)

@app.route("/api/<isbn>")
def book_api(isbn):
    book = db.execute("SELECT title, author, year, isbn, \
                    COUNT(reviews.id) as review_count, \
                    AVG(reviews.rating) as average_score \
                    FROM books \
                    INNER JOIN reviews \
                    ON books.id = reviews.book_id \
                    WHERE isbn = :isbn \
                    GROUP BY title, author, year, isbn",
                    {"isbn": isbn}).fetchone()
    
    if book is None:
        return jsonify({"error": "Invalid isbn"}), 422

    result = dict(book.items())
    result['average_score'] = float('%.2f'%(result['average_score']))
    
    return jsonify(result)