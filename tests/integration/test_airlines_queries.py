import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from src.core.text_to_sql_agent import TextToSQLAgent

def test_queries():
    """Test various queries to ensure proper handling"""
    
    agent = TextToSQLAgent()
    
    # Test queries - mix of valid and invalid
    test_queries = [
        "what is the capital of india",
        "how to cook pasta", 
        "what is 2+2",
        "Show me flights from Delhi to Mumbai",
        "Find the cheapest flights",
        "who is the president of india",
        "what is the weather like",
        "Show me flights with no stops"
    ]
    
    print("🧪 Testing Airlines Text-to-SQL Agent")
    print("=" * 50)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {query}")
        print("-" * 30)
        
        try:
            result = agent.process_query(query)
            
            print(f"Success: {result['success']}")
            print(f"Error Type: {result.get('error_type', 'N/A')}")
            
            if result['success']:
                print(f"Results: {len(result['data'])} rows found")
                print(f"SQL: {result['sql_query'][:100]}...")
            else:
                print(f"Response: {result['insights']}")
                
        except Exception as e:
            print(f"Exception: {e}")
        
        print()

if __name__ == "__main__":
    test_queries() 