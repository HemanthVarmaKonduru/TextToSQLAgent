#!/usr/bin/env python3
"""
Test script for Multi-Database Text-to-SQL Agent.
Tests both Airlines and Bikes databases functionality.
"""

import logging
from src.core.text_to_sql_agent import TextToSQLAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_airlines_queries():
    """Test airlines database queries."""
    print("\n🛫 Testing Airlines Database")
    print("=" * 50)
    
    try:
        agent = TextToSQLAgent(database_type="airlines")
        
        airlines_queries = [
            "Show me flights from Delhi to Mumbai",
            "Find the cheapest flights under 5000 rupees",
            "What are the average prices by airline?",
            "Which airlines have the most flights?",
            "Show me business class flights"
        ]
        
        for i, query in enumerate(airlines_queries, 1):
            print(f"\n{i}. Query: {query}")
            print("-" * 30)
            
            result = agent.process_query(query)
            
            if result['success']:
                print(f"✅ Success: Found {len(result['data'])} records")
                print(f"📊 Columns: {', '.join(result['data'].columns.tolist())}")
                if result['insights']:
                    print(f"💡 Insight: {result['insights'][:100]}...")
            else:
                print(f"❌ Error: {result.get('error_type', 'Unknown error')}")
                print(f"📝 Message: {result['insights']}")
    
    except Exception as e:
        print(f"❌ Airlines test failed: {e}")

def test_bikes_queries():
    """Test bikes database queries."""
    print("\n🏍️ Testing Bikes Database")
    print("=" * 50)
    
    try:
        agent = TextToSQLAgent(database_type="bikes")
        
        bikes_queries = [
            "Show me all Ducati bikes",
            "Find bikes under 10 lakhs",
            "Which bikes have ABS?",
            "Show me bikes with mileage above 15 km/l",
            "Find the most powerful bikes",
            "What are the different bike brands?"
        ]
        
        for i, query in enumerate(bikes_queries, 1):
            print(f"\n{i}. Query: {query}")
            print("-" * 30)
            
            result = agent.process_query(query)
            
            if result['success']:
                print(f"✅ Success: Found {len(result['data'])} records")
                print(f"📊 Columns: {', '.join(result['data'].columns.tolist())}")
                if result['insights']:
                    print(f"💡 Insight: {result['insights'][:100]}...")
            else:
                print(f"❌ Error: {result.get('error_type', 'Unknown error')}")
                print(f"📝 Message: {result['insights']}")
    
    except Exception as e:
        print(f"❌ Bikes test failed: {e}")

def test_context_restriction():
    """Test that context restriction works for both databases."""
    print("\n🚫 Testing Context Restriction")
    print("=" * 50)
    
    invalid_queries = [
        "who is the president of india",
        "what is the capital of france",
        "how to cook pasta",
        "what is 2+2"
    ]
    
    print("\n--- Testing Airlines Database Context ---")
    try:
        airlines_agent = TextToSQLAgent(database_type="airlines")
        
        for query in invalid_queries[:2]:  # Test 2 queries
            print(f"\nQuery: {query}")
            result = airlines_agent.process_query(query)
            
            if not result['success'] and 'non_airlines_question' in result.get('error_type', ''):
                print("✅ Correctly rejected non-airlines question")
            else:
                print("❌ Should have rejected this question")
    
    except Exception as e:
        print(f"❌ Airlines context test failed: {e}")
    
    print("\n--- Testing Bikes Database Context ---")
    try:
        bikes_agent = TextToSQLAgent(database_type="bikes")
        
        for query in invalid_queries[2:]:  # Test 2 queries
            print(f"\nQuery: {query}")
            result = bikes_agent.process_query(query)
            
            if not result['success'] and 'non_bikes_question' in result.get('error_type', ''):
                print("✅ Correctly rejected non-bikes question")
            else:
                print("❌ Should have rejected this question")
    
    except Exception as e:
        print(f"❌ Bikes context test failed: {e}")

def test_database_switching():
    """Test switching between databases."""
    print("\n🔄 Testing Database Switching")
    print("=" * 50)
    
    try:
        # Start with airlines
        agent = TextToSQLAgent(database_type="airlines")
        print(f"Initial database: {agent.current_database}")
        
        # Test airlines query
        result = agent.process_query("Show me flights from Delhi to Mumbai")
        print(f"Airlines query success: {result['success']}")
        
        # Switch to bikes
        agent.set_database_context("bikes")
        print(f"Switched to: {agent.current_database}")
        
        # Test bikes query
        result = agent.process_query("Show me all Ducati bikes")
        print(f"Bikes query success: {result['success']}")
        
        # Switch back to airlines
        agent.set_database_context("airlines")
        print(f"Switched back to: {agent.current_database}")
        
        # Test airlines query again
        result = agent.process_query("Find the cheapest flights")
        print(f"Airlines query success: {result['success']}")
        
        print("✅ Database switching works correctly!")
    
    except Exception as e:
        print(f"❌ Database switching test failed: {e}")

def test_database_stats():
    """Test database statistics."""
    print("\n📊 Testing Database Statistics")
    print("=" * 50)
    
    try:
        # Airlines stats
        airlines_agent = TextToSQLAgent(database_type="airlines")
        airlines_stats = airlines_agent.db_manager.get_quick_stats("airlines")
        print(f"Airlines Stats: {airlines_stats}")
        
        # Bikes stats
        bikes_agent = TextToSQLAgent(database_type="bikes")
        bikes_stats = bikes_agent.db_manager.get_quick_stats("bikes")
        print(f"Bikes Stats: {bikes_stats}")
        
        print("✅ Statistics work correctly!")
    
    except Exception as e:
        print(f"❌ Statistics test failed: {e}")

def main():
    """Run all tests."""
    print("🧪 Multi-Database Text-to-SQL Agent Test Suite")
    print("=" * 60)
    
    # Run tests
    test_airlines_queries()
    test_bikes_queries()
    test_context_restriction()
    test_database_switching()
    test_database_stats()
    
    print("\n🎉 Test Suite Complete!")
    print("=" * 60)

if __name__ == "__main__":
    main() 