# core/checkout.py - Fixed with absolute imports
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.connection import DatabaseConnection

class CheckoutManager:
    def __init__(self):
        self.db = DatabaseConnection()
    
    def checkout_item(self, item_id, employee_name, quantity=1, location='field', order_number=''):
        """Check out an item"""
        try:
            # Get or create employee
            emp = self.db.fetchone(
                "SELECT id FROM employees WHERE LOWER(employee_name) = LOWER(?)", 
                (employee_name,)
            )
            
            if not emp:
                self.db.execute(
                    "INSERT INTO employees (employee_name) VALUES (?)", 
                    (employee_name,)
                )
                emp = self.db.fetchone(
                    "SELECT id FROM employees WHERE employee_name = ?", 
                    (employee_name,)
                )
            
            employee_id = emp['id']
            
            # Check availability
            item = self.db.fetchone(
                "SELECT item_name, available FROM inventory WHERE id = ?", 
                (item_id,)
            )
            
            if not item:
                return False, "Item not found"
            
            if item['available'] < quantity:
                return False, f"Not enough available. Only {item['available']} in stock"
            
            # Create checkout record
            self.db.execute('''
                INSERT INTO checkouts 
                (item_id, employee_id, quantity, location, order_number)
                VALUES (?, ?, ?, ?, ?)
            ''', (item_id, employee_id, quantity, location, order_number))
            
            # Update availability
            self.db.execute(
                "UPDATE inventory SET available = available - ? WHERE id = ?",
                (quantity, item_id)
            )
            
            return True, f"Checked out {quantity} x {item['item_name']} to {employee_name}"
            
        except Exception as e:
            return False, str(e)
    
    def checkin_item(self, item_id, quantity=None):
        """Return an item"""
        try:
            # Find active checkout
            checkout = self.db.fetchone('''
                SELECT c.id, c.quantity, i.item_name, e.employee_name
                FROM checkouts c
                JOIN inventory i ON c.item_id = i.id
                JOIN employees e ON c.employee_id = e.id
                WHERE c.item_id = ? AND c.status = 'active'
                ORDER BY c.checkout_date DESC
            ''', (item_id,))
            
            if not checkout:
                return False, "No active checkout found for this item"
            
            return_qty = quantity or checkout['quantity']
            
            # Update checkout
            self.db.execute(
                "UPDATE checkouts SET status = 'returned', actual_return = CURRENT_TIMESTAMP WHERE id = ?",
                (checkout['id'],)
            )
            
            # Update availability
            self.db.execute(
                "UPDATE inventory SET available = available + ? WHERE id = ?",
                (return_qty, item_id)
            )
            
            return True, f"Returned {return_qty} x {checkout['item_name']} from {checkout['employee_name']}"
            
        except Exception as e:
            return False, str(e)
    
    def get_active_checkouts(self):
        """Get all active checkouts"""
        results = self.db.fetchall('''
            SELECT 
                c.id,
                i.id as item_id,
                i.item_name,
                i.brand,
                e.employee_name,
                c.quantity,
                c.checkout_date,
                c.location,
                c.order_number
            FROM checkouts c
            JOIN inventory i ON c.item_id = i.id
            JOIN employees e ON c.employee_id = e.id
            WHERE c.status = 'active'
            ORDER BY c.checkout_date DESC
        ''')
        
        return [dict(row) for row in results]