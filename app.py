from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    email = db.Column(db.String(120))

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    message = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(f"Received registration data - Username: {username}, Password: {password}")

        # Add validation
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            message = 'Username already taken, please choose another one.'
        else:
            # Store username and password
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()

            print("New user registered successfully.")
            session['username'] = username
            return redirect(url_for('user_details'))

    return render_template('register.html', message=message)

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if not user or user.password != password:
            message = 'Invalid username or password.'

        if user and user.password == password:
            return redirect(url_for('display_info', username=username))

    return render_template('login.html', message=message)

@app.route('/user-details', methods=['GET', 'POST'])
def user_details():
    if request.method == 'POST':
        # Process user details
        username = request.form['username']
        first_name = request.form['first']
        last_name = request.form['last']
        email = request.form['email']

        print(f"Updating details for user: {username}")  # Print statement

        # Store first name, last name, and email
        user = User.query.filter_by(username=username).first()
        if user:
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            db.session.commit()
            print("User details updated successfully.")
            return redirect(url_for('display_info', username=username))
        else:
            print(f"No user found with username: {username}")
    else:
        username =  session.get('username', None)
        return render_template('user-details.html', username=username)
    return render_template('user-details.html')

@app.route('/display-info/<username>')
def display_info(username):
    user = User.query.filter_by(username=username).first()
    if user:
        return render_template('display-info.html', user=user)

if __name__ == '__main__':
    app.run(debug=True)
