"""
Database utilities for the Airlines Text-to-SQL Agent.
Handles database connections, queries, and schema information.
"""

import logging
import pandas as pd
import psycopg2
from typing import Optional

from ..config.settings import settings

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database connections and operations."""
    
    def __init__(self):
        """Initialize the database manager."""
        self.connection_string = settings.get_database_url()
    
    def get_connection(self):
        """Get a database connection."""
        try:
            return psycopg2.connect(self.connection_string)
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def execute_query(self, sql_query: str) -> pd.DataFrame:
        """
        Execute SQL query and return results as DataFrame.
        
        Args:
            sql_query: SQL query to execute
            
        Returns:
            DataFrame with query results
        """
        try:
            conn = self.get_connection()
            df = pd.read_sql_query(sql_query, conn)
            conn.close()
            return df
        except Exception as e:
            logger.error(f"Error executing SQL query: {e}")
            raise
    
    def get_database_schema(self) -> str:
        """
        Get the database schema information for the LLM prompt.
        
        Returns:
            Formatted schema information string
        """
        schema_info = """
Database Schema:

1. airlines table:
   - airline_id (SERIAL PRIMARY KEY)
   - airline_name (VARCHAR(100) NOT NULL UNIQUE)
   - airline_code (VARCHAR(10))

2. cities table:
   - city_id (SERIAL PRIMARY KEY)
   - city_name (VARCHAR(100) NOT NULL UNIQUE)
   - country (VARCHAR(50) DEFAULT 'India')

3. flights table:
   - flight_id (SERIAL PRIMARY KEY)
   - index_id (INTEGER)
   - airline_id (INTEGER REFERENCES airlines(airline_id))
   - flight_number (VARCHAR(20))
   - source_city_id (INTEGER REFERENCES cities(city_id))
   - destination_city_id (INTEGER REFERENCES cities(city_id))
   - departure_time (VARCHAR(20))
   - arrival_time (VARCHAR(20))
   - stops (VARCHAR(20))
   - class_type (VARCHAR(20))
   - duration (DECIMAL(5,2))
   - days_left (INTEGER)
   - price (INTEGER)
   - created_at (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)

Relationships:
- flights.airline_id -> airlines.airline_id
- flights.source_city_id -> cities.city_id
- flights.destination_city_id -> cities.city_id

Sample Data:
- Airlines: SpiceJet, AirAsia, Vistara, Air India, GoAir, IndiGo
- Cities: Delhi, Mumbai, Bangalore, Hyderabad, Chennai, Kolkata, Pune, Ahmedabad
- Class Types: Economy, Business
- Stops: non-stop, 1 stop, 2 stops
"""
        return schema_info
    
    def test_connection(self) -> bool:
        """
        Test database connection.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            conn = self.get_connection()
            conn.close()
            logger.info("Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def get_sample_queries(self) -> list:
        """
        Get sample queries for the UI.
        
        Returns:
            List of sample queries
        """
        return [
            "Show me flights from Delhi to Mumbai",
            "Find the cheapest flights under 5000 rupees",
            "Which airlines fly to Bangalore?",
            "Show me business class flights",
            "Find flights with no stops",
            "What are the average prices by airline?",
            "Show me flights departing in the morning",
            "Which routes have the highest prices?"
        ] 