from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a strong secret key
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

client = MongoClient("mongodb://localhost:27017/")
db = client['test']

@app.route('/')
def home():
    # Check if the user is logged in by checking session data
    if 'username' in session:
        return render_template('home.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        # Check if the username already exists in the database
        user = db.users.find_one({'username': username})
        if user:
            return "User already exists!"

        # Insert the new user into the database
        db.users.insert_one({'username': username, 'password': hashed_password})
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Find the user by username
        user = db.users.find_one({'username': username})
        if user and check_password_hash(user['password'], password):
            session['username'] = username  # Store the username in session
            return redirect(url_for('home'))
        else:
            return "Invalid credentials"

    return render_template('login.html')

@app.route('/logout')
def logout():
    # Remove the username from session to log out
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
