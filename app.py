from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

# Initialize the Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Used for session management
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # SQLite database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Optional: disable the modification tracking
db = SQLAlchemy(app)

# Database model for Users
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    profile_pic = db.Column(db.String(150), default='default.jpg')  # Default profile picture
    likes = db.Column(db.Integer, default=0)  # Likes feature

# Create tables manually when the app starts (replaces before_first_request)
with app.app_context():
    db.create_all()

# Home page (redirect to login if not logged in)
@app.route('/')
def home():
    return redirect(url_for('login'))

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already taken!', 'danger')
            return redirect(url_for('register'))

        # Create new user
        new_user = User(username=username, password=password, email=email)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['user_id'] = user.id  # Store user ID in session
            return redirect(url_for('dashboard'))

        flash('Invalid credentials, try again.', 'danger')
    return render_template('login.html')

# Dashboard route (accessible only after login)
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    return render_template('dashboard.html', user=user)

# Profile route
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        user.email = request.form['email']
        user.profile_pic = request.form['profile_pic']  # Optionally update profile pic
        db.session.commit()
        flash('Profile updated successfully!', 'success')

    return render_template('profile.html', user=user)

# Like feature (allows a user to like once)
@app.route('/like')
def like():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])

    # Check if the user has already liked
    if user.likes == 0:
        user.likes = 1
        db.session.commit()
        flash('You liked this post!', 'success')
    else:
        flash('You can only like once.', 'warning')

    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
