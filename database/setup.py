# database/setup.py - Fixed with absolute imports
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.connection import DatabaseConnection
from config import DEFAULT_EMPLOYEES

def create_tables(db_connection):
    """Create all database tables"""
    
    # Create inventory table
    db_connection.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id TEXT,
            item_name TEXT NOT NULL,
            equipment TEXT,
            brand TEXT,
            stock INTEGER DEFAULT 0,
            available INTEGER DEFAULT 0,
            location TEXT DEFAULT 'workshop',
            notes TEXT
        )
    ''')
    
    # Create employees table
    db_connection.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_name TEXT NOT NULL UNIQUE,
            employee_id TEXT,
            department TEXT,
            active BOOLEAN DEFAULT 1
        )
    ''')
    
    # Create checkouts table
    db_connection.execute('''
        CREATE TABLE IF NOT EXISTS checkouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER,
            employee_id INTEGER,
            quantity INTEGER DEFAULT 1,
            checkout_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expected_return DATE,
            actual_return TIMESTAMP,
            location TEXT,
            order_number TEXT,
            status TEXT DEFAULT 'active',
            FOREIGN KEY (item_id) REFERENCES inventory(id),
            FOREIGN KEY (employee_id) REFERENCES employees(id)
        )
    ''')
    
    # Add default employees
    existing = db_connection.fetchone("SELECT COUNT(*) as count FROM employees")
    if existing['count'] == 0:
        for name, emp_id, dept in DEFAULT_EMPLOYEES:
            db_connection.execute(
                "INSERT INTO employees (employee_name, employee_id, department) VALUES (?, ?, ?)",
                (name, emp_id, dept)
            )
    
    print("✅ Database tables created")