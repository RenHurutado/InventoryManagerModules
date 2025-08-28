# llm/langchain_integration.py - Simple LLM integration for natural language queries
import sys
from pathlib import Path
import requests
import json

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import LLM_CONFIG
from database.connection import DatabaseConnection

class LLMManager:
    def __init__(self):
        self.lm_studio_url = LLM_CONFIG['lm_studio']['url']
        self.db = DatabaseConnection()
        self.connected = self.test_connection()
        
    def test_connection(self):
        """Test if LM Studio is running"""
        try:
            response = requests.get(self.lm_studio_url + "/v1/models", timeout=2)
            if response.status_code == 200:
                print("✅ Connected to LM Studio")
                return True
        except:
            pass
        print("⚠️ LM Studio not connected - start LM Studio to use natural language queries")
        return False
    
    def natural_language_to_sql(self, query):
        """Convert natural language to SQL"""
        if not self.connected:
            return None, "LM Studio not connected"
        
        # Create a prompt for the LLM
        prompt = f"""You are a SQL expert. Convert this natural language query to a SQLite query.

Database schema:
- inventory table: id, item_name, brand, equipment, stock, available, location, notes
- employees table: id, employee_name, employee_id, department
- checkouts table: id, item_id, employee_id, quantity, checkout_date, status, location, order_number

Natural language query: {query}

Return ONLY the SQL query, nothing else. No explanations, just the SQL.
SQL:"""
        
        try:
            # Call LM Studio
            response = requests.post(
                self.lm_studio_url + "/v1/completions",
                json={
                    "prompt": prompt,
                    "temperature": 0.1,
                    "max_tokens": 200,
                    "stop": ["\n\n", "Note:", "Explanation:"]
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                sql_query = result['choices'][0]['text'].strip()
                
                # Clean up the SQL query
                sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
                if sql_query.lower().startswith("sql:"):
                    sql_query = sql_query[4:].strip()
                
                return sql_query, None
            else:
                return None, f"LM Studio error: {response.status_code}"
                
        except Exception as e:
            return None, f"Error: {str(e)}"
    
    def execute_natural_language_query(self, query):
        """Execute a natural language query and return results"""
        # Convert to SQL
        sql_query, error = self.natural_language_to_sql(query)
        
        if error:
            return None, error
        
        print(f"📝 Generated SQL: {sql_query}")
        
        # Execute the SQL
        try:
            results = self.db.fetchall(sql_query)
            return results, None
        except Exception as e:
            return None, f"SQL execution error: {str(e)}"
    
    def process_command(self, user_input):
        """Process natural language commands (not just queries)"""
        if not self.connected:
            return "LM Studio not connected. Please start LM Studio first."
        
        # Determine if this is a query or a command
        prompt = f"""Analyze this user input and determine if it's:
1. A QUERY (asking for information)
2. A CHECKOUT command (checking out items)
3. A CHECKIN command (returning items)
4. An ADD command (adding new items)
5. OTHER

User input: {user_input}

Respond with just the category (QUERY, CHECKOUT, CHECKIN, ADD, or OTHER):"""
        
        try:
            response = requests.post(
                self.lm_studio_url + "/v1/completions",
                json={
                    "prompt": prompt,
                    "temperature": 0.1,
                    "max_tokens": 10
                }
            )
            
            category = response.json()['choices'][0]['text'].strip().upper()
            
            if "QUERY" in category:
                results, error = self.execute_natural_language_query(user_input)
                if error:
                    return f"❌ {error}"
                
                if not results:
                    return "No results found."
                
                # Format results nicely
                if results:
                    output = []
                    for row in results:
                        output.append(" | ".join(str(val) for val in dict(row).values()))
                    return "\n".join(output)
            
            elif "CHECKOUT" in category:
                return "To checkout items, use the 'checkout' command"
            
            elif "CHECKIN" in category:
                return "To return items, use 'checkin [item_id]'"
            
            elif "ADD" in category:
                return "To add new items, use the 'add' command"
            
            else:
                # Try to process as a query anyway
                results, error = self.execute_natural_language_query(user_input)
                if not error and results:
                    output = []
                    for row in results:
                        output.append(" | ".join(str(val) for val in dict(row).values()))
                    return "\n".join(output)
                else:
                    return "I couldn't understand that request. Try rephrasing or use the help command."
                    
        except Exception as e:
            return f"Error processing command: {str(e)}"