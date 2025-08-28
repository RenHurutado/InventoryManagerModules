# core/inventory.py - Fixed with absolute imports
import csv
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.connection import DatabaseConnection

class InventoryManager:
    def __init__(self):
        self.db = DatabaseConnection()
    
    def import_csv(self, csv_file):
        """Import inventory from CSV file"""
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                imported = 0
                
                for row in reader:
                    # Skip header rows
                    if row.get('Item Name', '') == 'Item Name':
                        continue
                    
                    item_name = row.get('Item Name', '').strip()
                    if not item_name:
                        continue
                    
                    # Insert item
                    self.db.execute('''
                        INSERT OR REPLACE INTO inventory 
                        (item_id, item_name, equipment, brand, stock, available, notes)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        row.get('Catalog ID', ''),
                        item_name,
                        row.get('Equipment', ''),
                        row.get('Brand', ''),
                        int(float(row.get('Stock', 0))),
                        int(float(row.get('Stock', 0))),  # available = stock initially
                        row.get('Notes', '')
                    ))
                    imported += 1
                
                print(f"✅ Imported {imported} items")
                return True
        except Exception as e:
            print(f"❌ Import error: {e}")
            return False
    
    def search_items(self, search_term=""):
        """Search for items"""
        if search_term:
            query = '''
                SELECT * FROM inventory 
                WHERE LOWER(item_name) LIKE ? 
                OR LOWER(brand) LIKE ?
                OR LOWER(equipment) LIKE ?
                ORDER BY item_name
            '''
            search_pattern = f'%{search_term.lower()}%'
            results = self.db.fetchall(query, (search_pattern, search_pattern, search_pattern))
        else:
            results = self.db.fetchall("SELECT * FROM inventory ORDER BY item_name")
        
        return [dict(row) for row in results]
    
    def add_item(self, item_data):
        """Add a new item"""
        try:
            self.db.execute('''
                INSERT INTO inventory 
                (item_name, brand, equipment, stock, available, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                item_data['item_name'],
                item_data.get('brand', ''),
                item_data.get('equipment', ''),
                item_data.get('stock', 0),
                item_data.get('stock', 0),
                item_data.get('notes', '')
            ))
            return True, "Item added successfully"
        except Exception as e:
            return False, str(e)
    
    def update_stock(self, item_id, new_stock):
        """Update item stock"""
        try:
            # Get current checked out quantity
            item = self.db.fetchone(
                "SELECT stock, available FROM inventory WHERE id = ?", 
                (item_id,)
            )
            if not item:
                return False, "Item not found"
            
            checked_out = item['stock'] - item['available']
            new_available = max(0, new_stock - checked_out)
            
            self.db.execute(
                "UPDATE inventory SET stock = ?, available = ? WHERE id = ?",
                (new_stock, new_available, item_id)
            )
            return True, "Stock updated"
        except Exception as e:
            return False, str(e)
    
    def get_summary(self):
        """Get inventory summary"""
        total = self.db.fetchone("SELECT COUNT(*) as count, SUM(stock) as total FROM inventory")
        available = self.db.fetchone("SELECT SUM(available) as total FROM inventory")
        low_stock = self.db.fetchone("SELECT COUNT(*) as count FROM inventory WHERE available <= 2")
        
        return {
            'total_items': total['count'] or 0,
            'total_stock': total['total'] or 0,
            'total_available': available['total'] or 0,
            'low_stock_items': low_stock['count'] or 0
        }