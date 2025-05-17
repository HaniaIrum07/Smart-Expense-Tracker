import sqlite3
from datetime import date
from flask import g

# Database configuration
DATABASE = 'budget_management.db'

def get_db():
    """Get a database connection with Row factory"""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys = ON;")
    return db

def init_db():
    """Initialize database tables"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # User table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS User (
                UserID TEXT PRIMARY KEY,
                Email TEXT UNIQUE NOT NULL,
                Password TEXT NOT NULL,
                Income REAL NOT NULL,
                OriginalIncome REAL NOT NULL
            );
        ''')
        
        # Expenses table
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
        
        # Transactions table
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
        
        conn.commit()

def close_connection(exception):
    """Close database connection"""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def insert_record(table_name, data_dict):
    """Insert a new record into the specified table"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            columns = ', '.join(data_dict.keys())
            placeholders = ', '.join(['?'] * len(data_dict))
            values = tuple(data_dict.values())

            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders});"
            cursor.execute(query, values)
            conn.commit()
            return True
    except sqlite3.Error as e:
        print(f"[INSERT ERROR] {e}")
        return False

def get_records(table_name, where_clause=None, where_values=()):
    """Fetch records from the specified table"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            query = f"SELECT * FROM {table_name}"
            if where_clause:
                query += f" WHERE {where_clause}"
            cursor.execute(query, where_values)
            return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"[FETCH ERROR] {e}")
        return []

def get_record(table_name, where_clause=None, where_values=()):
    """Fetch a single record"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            query = f"SELECT * FROM {table_name}"
            if where_clause:
                query += f" WHERE {where_clause} LIMIT 1"
            cursor.execute(query, where_values)
            return cursor.fetchone()
    except sqlite3.Error as e:
        print(f"[FETCH ERROR] {e}")
        return None

def update_record(table_name, update_dict, where_clause, where_values):
    """Update records in the specified table"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            set_clause = ', '.join([f"{key} = ?" for key in update_dict.keys()])
            values = tuple(update_dict.values()) + tuple(where_values)

            query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause};"
            cursor.execute(query, values)
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"[UPDATE ERROR] {e}")
        return False

def delete_record(table_name, where_clause, where_values):
    """Delete records from the specified table"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            query = f"DELETE FROM {table_name} WHERE {where_clause};"
            cursor.execute(query, where_values)
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"[DELETE ERROR] {e}")
        return False

def execute_query(query, params=()):
    """Execute a custom SQL query"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor
    except sqlite3.Error as e:
        print(f"[QUERY ERROR] {e}")
        return None

# Initialize database tables when this module is imported
with app.app_context():
    init_db()