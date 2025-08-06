"""
Database utilities for the Multi-Domain Text-to-SQL Agent.
Handles database connections, queries, and schema information for Airlines and Bikes databases.
"""

import psycopg2
import pandas as pd
import logging
from typing import Dict, List, Tuple, Optional
from src.config.settings import settings

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database connections and operations for multiple domains."""
    
    def __init__(self):
        """Initialize the database manager."""
        self.current_database = "airlines"  # Default database
        
    def get_connection(self) -> psycopg2.extensions.connection:
        """Get a database connection."""
        try:
            conn = psycopg2.connect(
                host=settings.DB_HOST,
                port=settings.DB_PORT,
                user=settings.DB_USER,
                password=settings.DB_PASSWORD,
                database=settings.DB_NAME
            )
            return conn
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            raise
    
    def execute_query(self, sql_query: str) -> pd.DataFrame:
        """Execute a SQL query and return results as a DataFrame."""
        try:
            conn = self.get_connection()
            df = pd.read_sql_query(sql_query, conn)
            conn.close()
            logger.info(f"Query executed successfully, returned {len(df)} rows")
            return df
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise
    
    def get_database_schema(self, database_type: str = None) -> str:
        """Get database schema information for the specified database type."""
        if database_type is None:
            database_type = self.current_database
            
        if database_type == "airlines":
            return self._get_airlines_schema()
        elif database_type == "bikes":
            return self._get_bikes_schema()
        else:
            return "Unknown database type"
    
    def _get_airlines_schema(self) -> str:
        """Get airlines database schema information."""
        return """
        Airlines Database Schema:
        
        1. airlines table:
           - airline_id (Primary Key)
           - airline_name (Airline name)
           - airline_code (Airline code)
        
        2. cities table:
           - city_id (Primary Key)
           - city_name (City name)
           - country (Country, default: India)
        
        3. flights table:
           - flight_id (Primary Key)
           - airline_id (Foreign Key to airlines)
           - source_city_id (Foreign Key to cities)
           - destination_city_id (Foreign Key to cities)
           - flight_number (Flight number)
           - departure_time (Departure time)
           - arrival_time (Arrival time)
           - stops (Number of stops)
           - class_type (Economy/Business)
           - duration (Flight duration in hours)
           - days_left (Days until departure)
           - price (Flight price in rupees)
        
        Sample Airlines Queries:
        - Show me flights from Delhi to Mumbai
        - Find the cheapest flights under 5000 rupees
        - Which airlines fly to Bangalore?
        - Show me business class flights
        - What are the average prices by airline?
        - Find flights with no stops
        - Show me flights departing in the morning"
        """
    
    def _get_bikes_schema(self) -> str:
        """Get bikes database schema information."""
        return """
        Bikes Database Schema:
        
        1. bike_brands table:
           - brand_id (Primary Key)
           - brand_name (Brand name like Ducati, BMW, etc.)
        
        2. bikes table:
           - bike_id (Primary Key)
           - bike_name (Full bike model name)
           - brand_id (Foreign Key to bike_brands)
           - engine_capacity (Engine displacement)
           - transmission (Transmission type)
           - colors (Available colors)
           - price (Price in rupees)
           - displacement (Engine displacement)
           - max_power (Maximum power output)
           - max_torque (Maximum torque)
           - top_speed (Maximum speed)
           - cylinders (Number of cylinders)
           - fuel_type (Petrol/Electric)
           - mileage (Fuel efficiency in km/l)
           - fuel_tank_capacity (Tank capacity)
           - kerb_weight (Weight in kg)
           - seat_height (Seat height in mm)
           - front_brake_type (Front brake type)
           - rear_brake_type (Rear brake type)
           - abs_available (ABS availability)
        
        Sample Bikes Queries:
        - Show me all Ducati bikes
        - Find bikes under 10 lakhs
        - Which bikes have ABS?
        - Show me bikes with mileage above 15 km/l
        - Find the most powerful bikes
        - Show me electric bikes
        - Which bikes have the highest top speed?"""
    
    def set_current_database(self, database_type: str):
        """Set the current database context."""
        if database_type in ["airlines", "bikes"]:
            self.current_database = database_type
            logger.info(f"Database context switched to: {database_type}")
        else:
            raise ValueError(f"Unsupported database type: {database_type}")
    
    def get_sample_queries(self, database_type: str = None) -> List[str]:
        """Get sample queries for the specified database type."""
        if database_type is None:
            database_type = self.current_database
            
        if database_type == "airlines":
            return [
                "Show me flights from Delhi to Mumbai",
                "Find the cheapest flights under 5000 rupees",
                "Which airlines fly to Bangalore?",
                "Show me business class flights",
                "What are the average prices by airline?",
                "Find flights with no stops",
                "Show me flights departing in the morning"
            ]
        elif database_type == "bikes":
            return [
                "Show me all Ducati bikes",
                "Find bikes under 10 lakhs",
                "Which bikes have ABS?",
                "Show me bikes with mileage above 15 km/l",
                "Find the most powerful bikes",
                "Show me electric bikes",
                "Which bikes have the highest top speed?"
            ]
        else:
            return []
    
    def get_quick_stats(self, database_type: str = None) -> Dict[str, int]:
        """Get quick statistics for the specified database."""
        if database_type is None:
            database_type = self.current_database
            
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            stats = {}
            
            if database_type == "airlines":
                cursor.execute("SELECT COUNT(*) FROM flights")
                stats['Total Flights'] = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM airlines")
                stats['Total Airlines'] = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM cities")
                stats['Total Cities'] = cursor.fetchone()[0]
                
                cursor.execute("SELECT AVG(price) FROM flights")
                avg_price = cursor.fetchone()[0]
                stats['Average Price'] = int(avg_price) if avg_price else 0
                
            elif database_type == "bikes":
                cursor.execute("SELECT COUNT(*) FROM bikes")
                stats['Total Bikes'] = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM bike_brands")
                stats['Total Brands'] = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM bikes WHERE abs_available = true")
                stats['Bikes with ABS'] = cursor.fetchone()[0]
                
                cursor.execute("SELECT AVG(mileage) FROM bikes WHERE mileage IS NOT NULL")
                avg_mileage = cursor.fetchone()[0]
                stats['Average Mileage'] = float(avg_mileage) if avg_mileage else 0
            
            cursor.close()
            conn.close()
            return stats
            
        except Exception as e:
            logger.error(f"Error getting stats for {database_type}: {e}")
            return {}
    
    def test_connection(self) -> bool:
        """Test the database connection."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            return result[0] == 1
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def get_available_databases(self) -> List[str]:
        """Get list of available database types."""
        return ["airlines", "bikes"]
    
    def get_database_description(self, database_type: str) -> str:
        """Get a description of the database."""
        descriptions = {
            "airlines": "Airlines Flight Information - Contains data about flights, airlines, cities, prices, schedules, and routes for domestic and international travel.",
            "bikes": "Motorcycle Information - Contains comprehensive data about bikes including specifications, performance, features, pricing, and technical details."
        }
        return descriptions.get(database_type, "Unknown database") 