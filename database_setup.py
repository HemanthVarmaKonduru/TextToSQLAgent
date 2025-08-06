"""
Database setup and initialization for the Multi-Domain Text-to-SQL Agent.
Supports Airlines and Bikes databases.
"""

import pandas as pd
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging
from src.config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_database():
    """Create the main database if it doesn't exist"""
    try:
        # Connect to default postgres database to create our database
        conn = psycopg2.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{settings.DB_NAME}'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f'CREATE DATABASE "{settings.DB_NAME}"')
            logger.info(f"Database '{settings.DB_NAME}' created successfully")
        else:
            logger.info(f"Database '{settings.DB_NAME}' already exists")
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Error creating database: {e}")
        raise

def create_airlines_tables():
    """Create tables for airlines data"""
    try:
        conn = psycopg2.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME
        )
        cursor = conn.cursor()
        
        # Drop existing tables
        cursor.execute("DROP TABLE IF EXISTS flights CASCADE")
        cursor.execute("DROP TABLE IF EXISTS airlines CASCADE")
        cursor.execute("DROP TABLE IF EXISTS cities CASCADE")
        
        # Create airlines table
        cursor.execute("""
            CREATE TABLE airlines (
                airline_id SERIAL PRIMARY KEY,
                airline_name VARCHAR(100) NOT NULL UNIQUE,
                airline_code VARCHAR(10)
            )
        """)
        
        # Create cities table
        cursor.execute("""
            CREATE TABLE cities (
                city_id SERIAL PRIMARY KEY,
                city_name VARCHAR(100) NOT NULL UNIQUE,
                country VARCHAR(50) DEFAULT 'India'
            )
        """)
        
        # Create flights table
        cursor.execute("""
            CREATE TABLE flights (
                flight_id SERIAL PRIMARY KEY,
                index_id INTEGER,
                airline_id INTEGER REFERENCES airlines(airline_id),
                flight_number VARCHAR(20),
                source_city_id INTEGER REFERENCES cities(city_id),
                destination_city_id INTEGER REFERENCES cities(city_id),
                departure_time VARCHAR(20),
                arrival_time VARCHAR(20),
                stops VARCHAR(20),
                class_type VARCHAR(20),
                duration DECIMAL(5,2),
                days_left INTEGER,
                price INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        logger.info("Airlines tables created successfully")
        
    except Exception as e:
        logger.error(f"Error creating airlines tables: {e}")
        raise

def create_bikes_tables():
    """Create tables for bikes data"""
    try:
        conn = psycopg2.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME
        )
        cursor = conn.cursor()
        
        # Drop existing tables
        cursor.execute("DROP TABLE IF EXISTS bikes CASCADE")
        cursor.execute("DROP TABLE IF EXISTS bike_brands CASCADE")
        
        # Create bike brands table
        cursor.execute("""
            CREATE TABLE bike_brands (
                brand_id SERIAL PRIMARY KEY,
                brand_name VARCHAR(50) NOT NULL UNIQUE
            )
        """)
        
        # Create bikes table with key specifications
        cursor.execute("""
            CREATE TABLE bikes (
                bike_id SERIAL PRIMARY KEY,
                bike_name VARCHAR(200) NOT NULL,
                brand_id INTEGER REFERENCES bike_brands(brand_id),
                engine_capacity VARCHAR(50),
                transmission VARCHAR(100),
                colors TEXT,
                price VARCHAR(50),
                displacement VARCHAR(50),
                max_power VARCHAR(100),
                max_torque VARCHAR(100),
                riding_range VARCHAR(50),
                top_speed VARCHAR(50),
                transmission_type VARCHAR(100),
                gear_shifting_pattern VARCHAR(50),
                cylinders INTEGER,
                fuel_type VARCHAR(50),
                mileage DECIMAL(5,2),
                fuel_tank_capacity VARCHAR(50),
                kerb_weight VARCHAR(50),
                seat_height VARCHAR(50),
                wheelbase VARCHAR(50),
                ground_clearance VARCHAR(50),
                front_brake_type VARCHAR(100),
                rear_brake_type VARCHAR(100),
                front_suspension VARCHAR(200),
                rear_suspension VARCHAR(200),
                tyre_type VARCHAR(50),
                headlight_type VARCHAR(50),
                start_type VARCHAR(50),
                abs_available BOOLEAN DEFAULT false,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        logger.info("Bikes tables created successfully")
        
    except Exception as e:
        logger.error(f"Error creating bikes tables: {e}")
        raise

def insert_airlines_data():
    """Insert airlines data from CSV"""
    try:
        # Read CSV data
        df = pd.read_csv('data/airlines_flights_data.csv')
        logger.info(f"Loaded {len(df)} flight records from CSV")
        
        conn = psycopg2.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME
        )
        cursor = conn.cursor()
        
        # Insert unique airlines
        unique_airlines = df['airline'].unique()
        for airline in unique_airlines:
            cursor.execute("""
                INSERT INTO airlines (airline_name) 
                VALUES (%s) 
                ON CONFLICT (airline_name) DO NOTHING
            """, (airline,))
        
        # Insert unique cities
        source_cities = df['source_city'].unique()
        destination_cities = df['destination_city'].unique()
        all_cities = set(list(source_cities) + list(destination_cities))
        
        for city in all_cities:
            cursor.execute("""
                INSERT INTO cities (city_name) 
                VALUES (%s) 
                ON CONFLICT (city_name) DO NOTHING
            """, (city,))
        
        conn.commit()
        
        # Insert flight data
        for index, row in df.iterrows():
            # Get airline_id
            cursor.execute("SELECT airline_id FROM airlines WHERE airline_name = %s", (row['airline'],))
            airline_id = cursor.fetchone()[0]
            
            # Get source city_id
            cursor.execute("SELECT city_id FROM cities WHERE city_name = %s", (row['source_city'],))
            source_city_id = cursor.fetchone()[0]
            
            # Get destination city_id
            cursor.execute("SELECT city_id FROM cities WHERE city_name = %s", (row['destination_city'],))
            destination_city_id = cursor.fetchone()[0]
            
            cursor.execute("""
                INSERT INTO flights (
                    index_id, airline_id, flight_number, source_city_id, destination_city_id,
                    departure_time, arrival_time, stops, class_type, duration, days_left, price
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                row['index'], airline_id, row.get('flight', 'N/A'), source_city_id, destination_city_id,
                row['departure_time'], row['arrival_time'], row['stops'], row['class'],
                row['duration'], row['days_left'], row['price']
            ))
        
        conn.commit()
        cursor.close()
        conn.close()
        logger.info("Airlines data inserted successfully")
        
    except Exception as e:
        logger.error(f"Error inserting airlines data: {e}")
        raise

def insert_bikes_data():
    """Insert bikes data from CSV"""
    try:
        # Read CSV data
        df = pd.read_csv('data/bike_information.csv')
        logger.info(f"Loaded {len(df)} bike records from CSV")
        
        conn = psycopg2.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME
        )
        cursor = conn.cursor()
        
        # Extract and insert unique brands
        brands = set()
        for bike_name in df['bike_name']:
            # Extract brand (first word before space)
            brand = bike_name.split()[0] if ' ' in bike_name else bike_name
            brands.add(brand)
        
        for brand in brands:
            cursor.execute("""
                INSERT INTO bike_brands (brand_name) 
                VALUES (%s) 
                ON CONFLICT (brand_name) DO NOTHING
            """, (brand,))
        
        conn.commit()
        
        # Insert bike data
        for index, row in df.iterrows():
            # Extract brand
            brand = row['bike_name'].split()[0] if ' ' in row['bike_name'] else row['bike_name']
            
            # Get brand_id
            cursor.execute("SELECT brand_id FROM bike_brands WHERE brand_name = %s", (brand,))
            brand_result = cursor.fetchone()
            brand_id = brand_result[0] if brand_result else None
            
            # Parse cylinders
            cylinders = None
            try:
                cylinders = int(row['Cylinders']) if pd.notna(row['Cylinders']) else None
            except:
                pass
            
            # Parse mileage
            mileage = None
            try:
                mileage = float(row['Mileage']) if pd.notna(row['Mileage']) else None
            except:
                pass
            
            # Check for ABS
            abs_available = 'ABS' in str(row.get('Braking System', ''))
            
            cursor.execute("""
                INSERT INTO bikes (
                    bike_name, brand_id, engine_capacity, transmission, colors, price,
                    displacement, max_power, max_torque, riding_range, top_speed,
                    transmission_type, gear_shifting_pattern, cylinders, fuel_type,
                    mileage, fuel_tank_capacity, kerb_weight, seat_height, wheelbase,
                    ground_clearance, front_brake_type, rear_brake_type, front_suspension,
                    rear_suspension, tyre_type, headlight_type, start_type, abs_available
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                row['bike_name'], brand_id, row.get('Engine Capacity'), row.get('Transmission_x'),
                row.get('colors'), row.get('price'), row.get('Displacement'), row.get('Max Power'),
                row.get('Max Torque'), row.get('Riding Range'), row.get('Top Speed'),
                row.get('Transmission Type'), row.get('Gear Shifting Pattern'), cylinders,
                row.get('Fuel Type'), mileage, row.get('Fuel Tank Capacity'), row.get('Kerb Weight'),
                row.get('Seat Height'), row.get('Wheelbase'), row.get('Ground Clearance'),
                row.get('Front Brake Type'), row.get('Rear Brake Type'), row.get('Front Suspension'),
                row.get('Rear Suspension'), row.get('Tyre Type'), row.get('Headlight Type'),
                row.get('Start Type'), abs_available
            ))
        
        conn.commit()
        cursor.close()
        conn.close()
        logger.info("Bikes data inserted successfully")
        
    except Exception as e:
        logger.error(f"Error inserting bikes data: {e}")
        raise

def get_airlines_schema():
    """Get airlines database schema information"""
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
    """

def get_bikes_schema():
    """Get bikes database schema information"""
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
    """

def get_sample_queries(database_type="airlines"):
    """Get sample queries for the specified database"""
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

def setup_complete_database():
    """Set up both airlines and bikes databases"""
    try:
        logger.info("Starting complete database setup...")
        
        # Create database
        create_database()
        
        # Create tables
        create_airlines_tables()
        create_bikes_tables()
        
        # Insert data
        insert_airlines_data()
        insert_bikes_data()
        
        logger.info("Complete database setup finished successfully!")
        
    except Exception as e:
        logger.error(f"Error in complete database setup: {e}")
        raise

if __name__ == "__main__":
    setup_complete_database() 