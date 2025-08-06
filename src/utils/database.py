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
        
        Table: bike_information
        Key columns for querying:
        - bike_name (TEXT) - Full bike model name
        - engine_capacity (TEXT) - Engine capacity (e.g., "999cc", "1000cc")
        - transmission_x (TEXT) - Primary transmission info
        - transmission_y (TEXT) - Secondary transmission info  
        - transmission_type (TEXT) - Transmission type
        - colors (TEXT) - Available colors
        - price (TEXT) - Price (contains ₹ symbol and commas)
        - displacement (TEXT) - Engine displacement
        - max_power (TEXT) - Maximum power output
        - max_torque (TEXT) - Maximum torque
        - top_speed (TEXT) - Maximum speed
        - cylinders (TEXT) - Number of cylinders
        - fuel_type (TEXT) - Fuel type (Petrol/Electric/etc.)
        - mileage (TEXT) - Fuel efficiency
        - fuel_tank_capacity (TEXT) - Tank capacity
        - kerb_weight (TEXT) - Weight
        - seat_height (TEXT) - Seat height
        - front_brake_type (TEXT) - Front brake type
        - rear_brake_type (TEXT) - Rear brake type
        - front_suspension (TEXT) - Front suspension
        - rear_suspension (TEXT) - Rear suspension
        - ground_clearance (TEXT) - Ground clearance
        - wheelbase (TEXT) - Wheelbase
        - overall_length (TEXT) - Overall length
        - overall_width (TEXT) - Overall width
        - overall_height (TEXT) - Overall height
        - headlight_type (TEXT) - Headlight type
        - start_type (TEXT) - Start mechanism
        - tyre_type (TEXT) - Tyre type
        - chassis_type (TEXT) - Chassis type
        - cooling_system (TEXT) - Cooling system
        - ignition (TEXT) - Ignition system
        - gear_shifting_pattern (TEXT) - Gear pattern
        - compression_ratio (TEXT) - Compression ratio
        - bore (TEXT) - Engine bore
        - stroke (TEXT) - Engine stroke
        - valves_per_cylinder (TEXT) - Valves per cylinder
        - clutch (TEXT) - Clutch type
        - fuel_delivery_system (TEXT) - Fuel delivery
        - emission_standard (TEXT) - Emission standard
        - braking_system (TEXT) - Braking system
        - front_brake_size (TEXT) - Front brake size
        - rear_brake_size (TEXT) - Rear brake size
        - calliper_type (TEXT) - Calliper type
        - wheel_type (TEXT) - Wheel type
        - front_wheel_size (TEXT) - Front wheel size
        - rear_wheel_size (TEXT) - Rear wheel size
        - front_tyre_size (TEXT) - Front tyre size
        - rear_tyre_size (TEXT) - Rear tyre size
        - additional_features (TEXT) - Additional features
        
        IMPORTANT NOTES:
        - All columns are TEXT type, use LIKE for pattern matching
        - For engine capacity queries like "1000CC bikes", use: WHERE engine_capacity LIKE '1,0%cc' OR engine_capacity LIKE '1,1%cc' (format is "1,103 cc")
        - For price comparisons, extract numbers: CAST(REGEXP_REPLACE(price, '[^0-9]', '', 'g') AS BIGINT)
        - For numeric comparisons on TEXT fields, use careful pattern matching
        
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
                "Show me all 1000CC bikes",
                "Find all Ducati bikes",
                "Show me bikes under 10 lakhs",
                "Which bikes have the best mileage?",
                "Find the most powerful bikes",
                "Show me electric bikes",
                "Which bikes have disc brakes?",
                "Show bikes with good fuel efficiency",
                "Find bikes by engine capacity"
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
                cursor.execute("SELECT COUNT(*) FROM bike_information")
                stats['Total Bikes'] = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(DISTINCT CASE WHEN bike_name LIKE '%Ducati%' THEN 'Ducati' WHEN bike_name LIKE '%BMW%' THEN 'BMW' WHEN bike_name LIKE '%Honda%' THEN 'Honda' WHEN bike_name LIKE '%Yamaha%' THEN 'Yamaha' WHEN bike_name LIKE '%KTM%' THEN 'KTM' END) FROM bike_information WHERE bike_name LIKE '%Ducati%' OR bike_name LIKE '%BMW%' OR bike_name LIKE '%Honda%' OR bike_name LIKE '%Yamaha%' OR bike_name LIKE '%KTM%'")
                brands_count = cursor.fetchone()[0]
                stats['Major Brands'] = brands_count if brands_count else 0
                
                cursor.execute("SELECT COUNT(*) FROM bike_information WHERE LOWER(front_brake_type) LIKE '%disc%' OR LOWER(rear_brake_type) LIKE '%disc%'")
                stats['Bikes with Disc Brakes'] = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM bike_information WHERE price IS NOT NULL AND price != ''")
                stats['Bikes with Price Info'] = cursor.fetchone()[0]
            
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