from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import joblib

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expense_tracker.db'
db = SQLAlchemy(app)

# Load the trained model and vectorizer
if os.path.exists('expense_category_model.pkl') and os.path.exists('expense_category_vectorizer.pkl'):
    model = joblib.load('expense_category_model.pkl')
    vectorizer = joblib.load('expense_category_vectorizer.pkl')
else:
    raise FileNotFoundError("Model or vectorizer not found. Train the model using train_model.py.")

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    cost = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(80), nullable=False)
    date = db.Column(db.Date, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Routes
@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully!')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        flash('Invalid email or password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    categories = Category.query.filter_by(user_id=user.id).all()
    return render_template('dashboard.html', user=user, categories=categories)

@app.route('/add_category', methods=['POST'])
def add_category():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 403

    name = request.form['name']
    user_id = session['user_id']

    new_category = Category(name=name, user_id=user_id)
    db.session.add(new_category)
    db.session.commit()

    return jsonify({'message': 'Category added successfully!'})

@app.route('/add_expense', methods=['POST'])
def add_expense():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 403

    try:
        name = request.form['name']
        cost = float(request.form['cost'])
        date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        category = request.form['category']

        # Validate cost
        if cost <= 0:
            return jsonify({'error': 'Cost must be a positive number'}), 400

        # Add expense to the database
        new_expense = Expense(name=name, cost=cost, category=category, date=date, user_id=session['user_id'])
        db.session.add(new_expense)
        db.session.commit()

        return jsonify({'message': 'Expense added successfully!', 'category': category})

    except ValueError as e:
        return jsonify({'error': 'Invalid input data'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_expenses/<date>', methods=['GET'])
def get_expenses(date):
    if 'user_id' not in session:
        return jsonify([]), 403
    
    try:
        user_id = session['user_id']
        expenses = Expense.query.filter_by(user_id=user_id, date=datetime.strptime(date, '%Y-%m-%d').date()).all()
        return jsonify([{'name': exp.name, 'cost': exp.cost, 'category': exp.category} for exp in expenses])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/monthly_report/<month>/<year>', methods=['GET'])
def monthly_report(month, year):
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 403

    try:
        # Validate month and year
        month = int(month)
        year = int(year)
        if month < 1 or month > 12 or year < 2000 or year > 2100:
            return jsonify({'error': 'Invalid month or year'}), 400

        user_id = session['user_id']
        expenses = Expense.query.filter(
            Expense.user_id == user_id,
            db.extract('month', Expense.date) == month,
            db.extract('year', Expense.date) == year
        ).all()

        category_totals = {}
        for expense in expenses:
            category_totals[expense.category] = category_totals.get(expense.category, 0) + expense.cost

        return jsonify(category_totals)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)