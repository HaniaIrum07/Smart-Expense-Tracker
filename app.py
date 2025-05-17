from flask import Flask, render_template, request, redirect, url_for, session, jsonify, g
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime, timedelta
import logging
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'your-very-secure-secret-key-change-this-in-production'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Database configuration
DATABASE = 'budget_management.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys = ON;")
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS User (
                UserID TEXT PRIMARY KEY,
                Email TEXT UNIQUE NOT NULL,
                Password TEXT NOT NULL,
                Income REAL NOT NULL,
                OriginalIncome REAL NOT NULL,
                CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Expenses (
                ExpenseID INTEGER PRIMARY KEY AUTOINCREMENT,
                UserID TEXT NOT NULL,
                Amount REAL NOT NULL,
                Category TEXT NOT NULL,
                Date DATE NOT NULL,
                Income REAL NOT NULL,
                FOREIGN KEY (UserID) REFERENCES User(UserID) ON DELETE CASCADE
            );
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Transactions (
                TransactionID INTEGER PRIMARY KEY AUTOINCREMENT,
                UserID TEXT NOT NULL,
                TransactionType TEXT NOT NULL,
                Amount REAL NOT NULL,
                Date DATE NOT NULL,
                FOREIGN KEY (UserID) REFERENCES User(UserID) ON DELETE CASCADE
            );
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS LoginAttempts (
                AttemptID INTEGER PRIMARY KEY AUTOINCREMENT,
                UserID TEXT,
                IPAddress TEXT NOT NULL,
                AttemptTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                Success BOOLEAN NOT NULL,
                FOREIGN KEY (UserID) REFERENCES User(UserID) ON DELETE CASCADE
            );
        ''')
        
        conn.commit()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userid = request.form.get('userid', '').strip()
        password = request.form.get('password', '')
        ip_address = request.remote_addr

        if not userid or not password:
            return render_template('login.html', error="Please fill in all fields")

        try:
            conn = get_db()
            
            conn.execute(
                'INSERT INTO LoginAttempts (UserID, IPAddress, Success) VALUES (?, ?, ?)',
                (userid, ip_address, False)
            )
            conn.commit()

            user = conn.execute(
                'SELECT * FROM User WHERE UserID = ?', (userid,)
            ).fetchone()

            if user and check_password_hash(user['Password'], password):
                conn.execute(
                    'UPDATE LoginAttempts SET Success = ? WHERE AttemptID = ?',
                    (True, conn.execute('SELECT last_insert_rowid()').fetchone()[0])
                )
                conn.commit()

                session.permanent = True
                session['user_id'] = user['UserID']
                session['email'] = user['Email']
                logger.info(f"User {userid} logged in successfully from IP {ip_address}")
                
                return redirect(request.args.get('next') or url_for('dashboard'))
            else:
                logger.warning(f"Failed login attempt for user {userid} from IP {ip_address}")
                return render_template('login.html', error="Invalid username or password")

        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return render_template('login.html', error="Login failed. Please try again.")

    registered = request.args.get('registered') == 'true'
    return render_template('login.html', registered=registered)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    
    try:
        data = request.form
        userid = data.get('userid', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')
        income = data.get('income', '0')

        if not all([userid, email, password, confirm_password, income]):
            return jsonify({'success': False, 'message': 'All fields are required'})

        if len(password) != 8:
            return jsonify({'success': False, 'message': 'Password must be exactly 8 characters'})

        if password != confirm_password:
            return jsonify({'success': False, 'message': 'Passwords do not match'})

        try:
            income = float(income)
            if income <= 0:
                return jsonify({'success': False, 'message': 'Income must be positive'})
        except ValueError:
            return jsonify({'success': False, 'message': 'Invalid income value'})

        conn = get_db()
        existing_user = conn.execute(
            'SELECT 1 FROM User WHERE UserID = ? OR Email = ?', (userid, email)
        ).fetchone()
        
        if existing_user:
            logger.warning(f"Registration attempt with existing user: {userid} or email: {email}")
            return jsonify({'success': False, 'message': 'User ID or Email already exists'})

        hashed_pw = generate_password_hash(password)
        conn.execute(
            'INSERT INTO User (UserID, Email, Password, Income, OriginalIncome) VALUES (?, ?, ?, ?, ?)',
            (userid, email, hashed_pw, income, income)
        )
        conn.commit()
        logger.info(f"New user registered: {userid}")

        return jsonify({
            'success': True,
            'message': 'Registration successful! Redirecting to login...',
            'redirect': url_for('login', registered='true')
        })
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'success': False, 'message': 'Registration failed. Please try again.'})

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    
    try:
        conn = get_db()
        user = conn.execute(
            'SELECT * FROM User WHERE UserID = ?', (user_id,)
        ).fetchone()
        
        if not user:
            session.clear()
            return redirect(url_for('login'))

        today = datetime.today().date()
        first_day = today.replace(day=1)

        expenses = conn.execute(
            'SELECT * FROM Expenses WHERE UserID = ? AND Date BETWEEN ? AND ?',
            (user_id, first_day, today)
        ).fetchall()

        transactions = conn.execute(
            'SELECT * FROM Transactions WHERE UserID = ? AND Date BETWEEN ? AND ?',
            (user_id, first_day, today)
        ).fetchall()

        # Convert to dictionaries for the template
        user_dict = dict(user)
        expenses_list = [dict(e) for e in expenses]
        transactions_list = [dict(t) for t in transactions]
        
        # Add additional data needed by the dashboard template
        user_dict['expenses'] = expenses_list
        user_dict['transactions'] = transactions_list
        
        return render_template('dashboard.html', 
            user=user_dict,
            expenses=expenses_list,
            transactions=transactions_list)
            
    except Exception as e:
        logger.error(f"Dashboard error for user {user_id}: {str(e)}")
        return render_template('error.html', error="Could not load dashboard data")

@app.route('/logout')
def logout():
    user_id = session.get('user_id')
    session.clear()
    logger.info(f"User {user_id} logged out")
    return redirect(url_for('login'))

# Add API endpoints needed by dashboard.html
@app.route('/api/update_user', methods=['POST'])
@login_required
def update_user():
    data = request.json
    field = data.get('field')
    value = data.get('value')
    
    if not field or value is None:
        return jsonify({'success': False, 'message': 'Invalid request'})
    
    try:
        conn = get_db()
        user_id = session['user_id']
        
        if field == 'income':
            conn.execute(
                'UPDATE User SET Income = ? WHERE UserID = ?',
                (float(value), user_id)
            )
        elif field == 'password':
            hashed_pw = generate_password_hash(value)
            conn.execute(
                'UPDATE User SET Password = ? WHERE UserID = ?',
                (hashed_pw, user_id)
            )
        # Add other fields as needed
            
        conn.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        logger.error(f"Update user error: {str(e)}")
        return jsonify({'success': False, 'message': 'Update failed'})

# Initialize database tables
init_db()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)