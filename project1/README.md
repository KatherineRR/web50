# Project 1

## Web Programming with Python and JavaScript

## About

Book Review Website

## Files

* Templates: This folder contains 7 html files with jinja2 code. The main one is layout.html that contains the aesthetic basis of the web application in case the user has logged in or not.
* Static: This folder contains a css file.

## Usage

* Register
* Log in
* Search books by name, author or ISBN
* Get info about a book
* Submit your own review and see those of others!

![](https://i.imgur.com/fgXGwVH.png)

![](https://i.imgur.com/fjk4yfy.png)

![](https://i.imgur.com/Wa2BJv8.png)


## :gear: Setup your own

```bash
# Clone repo
$ git clone https://github.com/me50/KatherineRR

$ cd project1

# Activate the virtualenv
$ source myvirtualenv/bin/activate (Linux)

# Install all dependencies
$ pip install -r requirements.txt

# ENV Variables
$ export FLASK_APP = application.py # flask run
$ export DATABASE_URL = Heroku Postgres DB URI
$ export GOODREADS_KEY = Goodreads API Key. # More info: https://www.goodreads.com/api
```
### Author
* Katherine Rodríguez Ramírez
