# cli.py - Enhanced CLI with LLM support
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from core.inventory import InventoryManager
from core.checkout import CheckoutManager

# Try to import LLM support
try:
    from llm.langchain_integration import LLMManager
    LLM_AVAILABLE = True
except:
    LLM_AVAILABLE = False

class SimpleCLI:
    def __init__(self):
        self.inventory = InventoryManager()
        self.checkout = CheckoutManager()
        self.llm = None
        
        # Initialize LLM if available
        if LLM_AVAILABLE:
            try:
                self.llm = LLMManager()
            except:
                print("⚠️ LLM initialization failed")
    
    def run(self):
        """Run the CLI"""
        print("\n🔧 WORKSHOP INVENTORY SYSTEM")
        print("=" * 40)
        
        if self.llm and self.llm.connected:
            print("🤖 LLM Mode: ENABLED")
            print("   - Use natural language queries")
            print("   - Or prefix with 'query:' for LLM processing")
        else:
            print("🤖 LLM Mode: DISABLED")
            print("   - Start LM Studio to enable natural language queries")
        
        print("\nType 'help' for commands or 'exit' to quit\n")
        
        while True:
            try:
                # Show different prompt if LLM is active
                if self.llm and self.llm.connected:
                    prompt = "🤖 >>> "
                else:
                    prompt = ">>> "
                
                command = input(prompt).strip()
                
                if not command:
                    continue
                
                # Handle exit
                if command.lower() in ['exit', 'quit']:
                    print("Goodbye!")
                    break
                
                # Check if it's an LLM query
                if self.llm and self.llm.connected:
                    # Direct LLM query with prefix
                    if command.lower().startswith('query:'):
                        query = command[6:].strip()
                        print("🔄 Processing query...")
                        result = self.llm.process_command(query)
                        print(result)
                        print()
                        continue
                    
                    # Try natural language if it doesn't match any command
                    command_lower = command.lower()
                    known_commands = ['help', 'search', 'all', 'summary', 'checkout', 
                                    'checkin', 'active', 'add', 'import']
                    
                    if not any(command_lower.startswith(cmd) for cmd in known_commands):
                        # Might be a natural language query
                        print("🔄 Processing natural language query...")
                        result = self.llm.process_command(command)
                        print(result)
                        print()
                        continue
                
                # Process regular commands
                self.process_command(command)
                
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit")
            except Exception as e:
                print(f"Error: {e}")
    
    def process_command(self, command):
        """Process regular commands"""
        command_lower = command.lower()
        
        if command_lower == 'help':
            self.show_help()
        
        elif command_lower.startswith('search'):
            search_term = command[6:].strip()
            self.search_items(search_term)
        
        elif command_lower == 'all':
            self.search_items("")
        
        elif command_lower == 'summary':
            self.show_summary()
        
        elif command_lower == 'checkout':
            self.checkout_interactive()
        
        elif command_lower.startswith('checkin'):
            parts = command.split()
            if len(parts) > 1:
                try:
                    item_id = int(parts[1])
                    self.checkin_item(item_id)
                except ValueError:
                    print("Usage: checkin [item_id]")
            else:
                print("Usage: checkin [item_id]")
        
        elif command_lower == 'active':
            self.show_active_checkouts()
        
        elif command_lower == 'add':
            self.add_item()
        
        elif command_lower.startswith('import'):
            parts = command.split(maxsplit=1)
            if len(parts) > 1:
                filename = parts[1]
                self.inventory.import_csv(filename)
            else:
                print("Usage: import [filename.csv]")
        
        elif command_lower == 'llm':
            self.toggle_llm()
        
        else:
            print("Unknown command. Type 'help' for commands.")
        
        print()  # Empty line for readability
    
    def show_help(self):
        """Show help"""
        print("\n📋 COMMANDS:")
        print("\n🔍 Search & View:")
        print("  search [term] - Search for items")
        print("  all          - Show all items")
        print("  summary      - Show inventory summary")
        print("  active       - Show active checkouts")
        
        print("\n📤 Check Out/In:")
        print("  checkout     - Check out an item")
        print("  checkin [id] - Return an item")
        
        print("\n📝 Management:")
        print("  add          - Add new item")
        print("  import [file]- Import CSV file")
        
        if self.llm and self.llm.connected:
            print("\n🤖 LLM Queries:")
            print("  query: [text]     - Force LLM processing")
            print("  Or just type naturally:")
            print("  - 'show all items with low stock'")
            print("  - 'what did Juan check out?'")
            print("  - 'items checked out to field'")
        
        print("\n⚙️ System:")
        print("  llm          - Toggle LLM mode")
        print("  help         - Show this help")
        print("  exit         - Quit")
    
    def toggle_llm(self):
        """Toggle LLM mode"""
        if not LLM_AVAILABLE:
            print("LLM module not available. Check installation.")
            return
        
        if not self.llm:
            self.llm = LLMManager()
        
        if self.llm.connected:
            self.llm.connected = False
            print("🤖 LLM Mode: DISABLED")
        else:
            self.llm.connected = self.llm.test_connection()
            if self.llm.connected:
                print("🤖 LLM Mode: ENABLED")
    
    def search_items(self, search_term):
        """Search and display items"""
        items = self.inventory.search_items(search_term)
        
        if not items:
            print("No items found")
            return
        
        print(f"\n{'ID':<5} {'Name':<30} {'Brand':<15} {'Avail/Stock':<12}")
        print("-" * 65)
        
        for item in items:
            print(f"{item['id']:<5} {item['item_name'][:30]:<30} "
                  f"{(item['brand'] or '')[:15]:<15} "
                  f"{item['available']}/{item['stock']}")
    
    def show_summary(self):
        """Show inventory summary"""
        stats = self.inventory.get_summary()
        print("\n📊 INVENTORY SUMMARY:")
        print(f"Total items: {stats['total_items']}")
        print(f"Total stock: {stats['total_stock']}")
        print(f"Available: {stats['total_available']}")
        print(f"Low stock items: {stats['low_stock_items']}")
    
    def checkout_interactive(self):
        """Interactive checkout"""
        # Search for item
        search = input("Search for item: ")
        items = self.inventory.search_items(search)
        
        if not items:
            print("No items found")
            return
        
        # Show items
        for i, item in enumerate(items[:10], 1):
            print(f"{i}. {item['item_name']} ({item['brand']}) - Available: {item['available']}")
        
        # Select item
        try:
            choice = int(input(f"Select item (1-{min(10, len(items))}): "))
            item = items[choice - 1]
        except:
            print("Invalid selection")
            return
        
        # Get details
        employee = input("Employee name: ")
        quantity = int(input("Quantity (default 1): ") or "1")
        location = input("Location (default: field): ") or "field"
        order = input("Order number: ")
        
        # Checkout
        success, message = self.checkout.checkout_item(
            item['id'], employee, quantity, location, order
        )
        print(message)
    
    def checkin_item(self, item_id):
        """Return an item"""
        success, message = self.checkout.checkin_item(item_id)
        print(message)
    
    def show_active_checkouts(self):
        """Show active checkouts"""
        checkouts = self.checkout.get_active_checkouts()
        
        if not checkouts:
            print("No active checkouts")
            return
        
        print(f"\n{'ID':<5} {'Item':<25} {'Employee':<20} {'Qty':<5} {'Date':<12}")
        print("-" * 70)
        
        for co in checkouts:
            date = co['checkout_date'][:10] if co['checkout_date'] else ''
            print(f"{co['item_id']:<5} {co['item_name'][:25]:<25} "
                  f"{co['employee_name'][:20]:<20} {co['quantity']:<5} {date}")
    
    def add_item(self):
        """Add new item"""
        print("\n➕ ADD NEW ITEM")
        item_data = {
            'item_name': input("Item name: "),
            'brand': input("Brand: "),
            'equipment': input("Equipment type: "),
            'stock': int(input("Stock quantity: ") or "0"),
            'notes': input("Notes: ")
        }
        
        success, message = self.inventory.add_item(item_data)
        print(message)