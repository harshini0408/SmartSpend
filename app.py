from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import joblib

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expense_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutes session timeout

db = SQLAlchemy(app)

# Load the trained model and vectorizer safely
model, vectorizer = None, None
try:
    if os.path.exists('expense_category_model.pkl'):
        model = joblib.load('expense_category_model.pkl')
        print("✅ Model loaded successfully")
    else:
        print("❌ Model file not found!")

    if os.path.exists('expense_category_vectorizer.pkl'):
        vectorizer = joblib.load('expense_category_vectorizer.pkl')
        print("✅ Vectorizer loaded successfully")
    else:
        print("❌ Vectorizer file not found!")
except Exception as e:
    print(f"❌ Error loading model: {e}")

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    income = db.Column(db.Float, nullable=True, default=0)
    spending_limit = db.Column(db.Float, nullable=True, default=0)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    cost = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(80), nullable=False)  # AI assigns this
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
        password = request.form['password']

        if User.query.filter_by(email=email).first():
            flash('Email already registered.')
            return redirect(url_for('signup'))
        
        if User.query.filter_by(username=username).first():
            flash('Username already taken.')
            return redirect(url_for('signup'))

        new_user = User(username=username, email=email, password=generate_password_hash(password))
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
            session.permanent = True
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

    user = db.session.get(User, session['user_id'])
    
    if not user:
        session.pop('user_id', None)
        flash("Session expired or invalid. Please log in again.", "error")
        return redirect(url_for('login'))
    
    expenses = Expense.query.filter_by(user_id=user.id).order_by(Expense.date.desc()).all()
    return render_template('dashboard.html', user=user, expenses=expenses)

@app.route('/add_expense', methods=['POST'])
def add_expense():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 403
    try:
        name = request.form['name']
        cost = float(request.form['cost'])
        date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()

        # AI Auto-Categorization
        category = "Uncategorized"
        if model and vectorizer:
            try:
                input_text = [name.lower()]
                input_vector = vectorizer.transform(input_text)
                category = model.predict(input_vector)[0]
                print(f"🔍 AI Predicted Category: {category}")
            except Exception as e:
                print(f"❌ AI Prediction Failed: {e}")

        new_expense = Expense(name=name, cost=cost, category=category, date=date, user_id=session['user_id'])
        db.session.add(new_expense)
        db.session.commit()

        return jsonify({'message': f'Expense added successfully! Categorized as {category}', 'category': category})

    except ValueError:
        return jsonify({'error': 'Invalid input data'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_expenses/<date>')
def get_expenses(date):
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 403
    expenses = Expense.query.filter_by(user_id=session['user_id'], date=date).all()
    return jsonify([{'name': e.name, 'cost': e.cost, 'category': e.category} for e in expenses])

@app.route('/monthly_report/<month>/<year>')
def monthly_report(month, year):
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 403
    
    user = db.session.get(User, session['user_id'])
    
    if not user:
        return jsonify({'error': 'User not found'}), 404

    expenses = Expense.query.filter(
        Expense.user_id == user.id,
        db.func.strftime('%m', Expense.date) == month,
        db.func.strftime('%Y', Expense.date) == year
    ).all()
    
    category_totals = {}
    for expense in expenses:
        category_totals[expense.category] = category_totals.get(expense.category, 0) + expense.cost

    return jsonify(category_totals)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
