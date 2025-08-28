# main.py - Fixed with proper imports
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from database.connection import DatabaseConnection
from database.setup import create_tables
from cli import SimpleCLI

def main():
    """Main function"""
    print("🔧 Starting Workshop Inventory System...")
    
    # Setup database
    db = DatabaseConnection()
    create_tables(db)
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--import' and len(sys.argv) > 2:
            # Import CSV file
            from core.inventory import InventoryManager
            inv = InventoryManager()
            inv.import_csv(sys.argv[2])
            return
    
    # Run CLI
    cli = SimpleCLI()
    cli.run()

if __name__ == "__main__":
    main()