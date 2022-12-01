import os

from flask import Flask, render_template, session, redirect, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from collections import deque
from helpers import login_required

app = Flask(__name__)
app.config["SECRET_KEY"] = "Lya and Tobby"
socketio = SocketIO(app)

channels = []
users = []
channelsMessages= dict()

@app.route("/")
@login_required
def index():
    return render_template("index.html", channels = channels)

@app.route("/signin", methods=["GET", "POST"])
def signin(): 
    """Log user in"""
 
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        if not request.form.get("username"):
            return render_template("error.html", message="must provide username")
        
        if request.form.get("username") in users:
            return render_template("error.html", message="that username already exists!")       
        
        users.append(request.form.get("username"))

        session['username'] = request.form.get("username")

        # Remember the user session on a cookie if the browser is closed.
        session.permanent = True

        return redirect("/")

    else:
        return render_template("signin.html")

@app.route("/logout", methods=['GET'])
@login_required
def logout():
    """ Logout user from list and delete cookie."""

    # Remove from list
    try:
        users.remove(session['username'])
    except ValueError:
        pass

    # Delete cookie
    session.clear()

    return redirect("/")

@app.route("/create", methods=["GET", "POST"])
@login_required
def create(): 

    if request.method == "POST":

        if not request.form.get("channel"):
            return render_template("error.html", message="must provide a name for the new chat")
        
        if request.form.get("channel") in channels:
            return render_template("error.html", message="that channel already exists!")       
        
        channels.append(request.form.get("channel"))

        channelsMessages[request.form.get("channel")] = deque()

        return redirect("/channels/" + request.form.get("channel"))

    else:
        return render_template("index.html", channels = channels)

@app.route("/channels/<channel>", methods=['GET', 'POST'])
@login_required
def enter_channel(channel):
    """ Show channel page to send and receive messages """

    # Updates user current channel
    session['current_channel'] = channel

    if request.method == "POST":       
        return redirect("/")
    
    return render_template("channel.html", channels = channels, messages=channelsMessages[channel])

@socketio.on('send message')
def send_msg(message, timestamp):
    """ Receive message with timestamp and broadcast on the channel """

    room = session.get('current_channel')

    if len(channelsMessages[room]) > 100:
        # Pop the oldest message
        channelsMessages[room].popleft()

    channelsMessages[room].append([timestamp, session.get('username'), message])

    emit('announce message', {
        'user': session.get('username'),
        'timestamp': timestamp,
        'msg': message}, 
        room = room)

@socketio.on("joined")
def joined():
    # Send message to announce that user has entered the channel

    join_room(session.get('current_channel'))
    
    emit('status', {
        'userJoined': session.get('username'),
        'channel': session.get('current_channel'),
        'msg': session.get('username') + ' has entered the channel'}, 
        room = session.get('current_channel'))