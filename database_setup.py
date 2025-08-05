import psycopg2
from psycopg2 import sql
import pandas as pd
from config import DATABASE_URL
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_database():
    """Create the database and airlines tables with data"""
    
    # Connect to PostgreSQL
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Create airlines tables
        create_tables_sql = """
        -- Drop tables if they exist
        DROP TABLE IF EXISTS flights CASCADE;
        DROP TABLE IF EXISTS airlines CASCADE;
        DROP TABLE IF EXISTS cities CASCADE;
        
        -- Create airlines table
        CREATE TABLE airlines (
            airline_id SERIAL PRIMARY KEY,
            airline_name VARCHAR(100) NOT NULL UNIQUE,
            airline_code VARCHAR(10)
        );
        
        -- Create cities table
        CREATE TABLE cities (
            city_id SERIAL PRIMARY KEY,
            city_name VARCHAR(100) NOT NULL UNIQUE,
            country VARCHAR(50) DEFAULT 'India'
        );
        
        -- Create flights table
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
        );
        
        -- Create indexes for better performance
        CREATE INDEX idx_flights_airline ON flights(airline_id);
        CREATE INDEX idx_flights_source ON flights(source_city_id);
        CREATE INDEX idx_flights_destination ON flights(destination_city_id);
        CREATE INDEX idx_flights_price ON flights(price);
        CREATE INDEX idx_flights_days_left ON flights(days_left);
        """
        
        cursor.execute(create_tables_sql)
        conn.commit()
        logger.info("Airlines tables created successfully")
        
        # Load and insert airlines data
        insert_airlines_data(cursor, conn)
        
        cursor.close()
        conn.close()
        logger.info("Airlines database setup completed successfully!")
        
    except Exception as e:
        logger.error(f"Error setting up database: {e}")
        raise

def insert_airlines_data(cursor, conn):
    """Load airlines data from CSV and insert into database"""
    
    try:
        # Read the CSV file
        logger.info("Loading airlines data from CSV...")
        df = pd.read_csv('airlines_flights_data.csv')
        
        # Clean and prepare data
        df = df.dropna()  # Remove any null values
        
        # Extract unique airlines
        unique_airlines = df['airline'].unique()
        logger.info(f"Found {len(unique_airlines)} unique airlines")
        
        # Insert airlines
        for airline in unique_airlines:
            cursor.execute(
                "INSERT INTO airlines (airline_name) VALUES (%s) ON CONFLICT (airline_name) DO NOTHING",
                (airline,)
            )
        
        # Extract unique cities (both source and destination)
        source_cities = df['source_city'].unique()
        dest_cities = df['destination_city'].unique()
        all_cities = list(set(list(source_cities) + list(dest_cities)))
        logger.info(f"Found {len(all_cities)} unique cities")
        
        # Insert cities
        for city in all_cities:
            cursor.execute(
                "INSERT INTO cities (city_name) VALUES (%s) ON CONFLICT (city_name) DO NOTHING",
                (city,)
            )
        
        conn.commit()
        logger.info("Airlines and cities inserted successfully")
        
        # Now insert flights data
        logger.info("Inserting flights data...")
        
        # Get airline and city mappings
        cursor.execute("SELECT airline_id, airline_name FROM airlines")
        airline_map = {row[1]: row[0] for row in cursor.fetchall()}
        
        cursor.execute("SELECT city_id, city_name FROM cities")
        city_map = {row[1]: row[0] for row in cursor.fetchall()}
        
        # Insert flights in batches
        batch_size = 1000
        total_rows = len(df)
        
        for i in range(0, total_rows, batch_size):
            batch_df = df.iloc[i:i+batch_size]
            
            for _, row in batch_df.iterrows():
                try:
                    cursor.execute("""
                        INSERT INTO flights (
                            index_id, airline_id, flight_number, source_city_id, 
                            destination_city_id, departure_time, arrival_time, 
                            stops, class_type, duration, days_left, price
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        row['index'],
                        airline_map.get(row['airline']),
                        row['flight'],
                        city_map.get(row['source_city']),
                        city_map.get(row['destination_city']),
                        row['departure_time'],
                        row['arrival_time'],
                        row['stops'],
                        row['class'],
                        row['duration'],
                        row['days_left'],
                        row['price']
                    ))
                except Exception as e:
                    logger.warning(f"Error inserting row {row['index']}: {e}")
                    continue
            
            conn.commit()
            logger.info(f"Inserted batch {i//batch_size + 1}/{(total_rows + batch_size - 1)//batch_size}")
        
        # Get final statistics
        cursor.execute("SELECT COUNT(*) FROM flights")
        flight_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM airlines")
        airline_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM cities")
        city_count = cursor.fetchone()[0]
        
        logger.info(f"Database populated successfully!")
        logger.info(f"Total flights: {flight_count}")
        logger.info(f"Total airlines: {airline_count}")
        logger.info(f"Total cities: {city_count}")
        
    except Exception as e:
        logger.error(f"Error loading airlines data: {e}")
        raise

def get_database_schema():
    """Get the airlines database schema information"""
    schema_info = """
    Airlines Database Schema:
    
    Table: airlines
    - airline_id (SERIAL PRIMARY KEY)
    - airline_name (VARCHAR(100) UNIQUE)
    - airline_code (VARCHAR(10))
    
    Table: cities
    - city_id (SERIAL PRIMARY KEY)
    - city_name (VARCHAR(100) UNIQUE)
    - country (VARCHAR(50) DEFAULT 'India')
    
    Table: flights
    - flight_id (SERIAL PRIMARY KEY)
    - index_id (INTEGER)
    - airline_id (INTEGER, REFERENCES airlines(airline_id))
    - flight_number (VARCHAR(20))
    - source_city_id (INTEGER, REFERENCES cities(city_id))
    - destination_city_id (INTEGER, REFERENCES cities(city_id))
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
    
    Sample Queries:
    - "Show me flights from Delhi to Mumbai"
    - "Find the cheapest flights"
    - "Which airlines fly to Bangalore?"
    - "Show me flights with no stops"
    - "What are the average prices by airline?"
    - "Find flights departing in the morning"
    - "Show me business class flights"
    - "Which routes have the highest prices?"
    """
    return schema_info

def get_sample_queries():
    """Get sample queries for the airlines database"""
    return [
        "Show me flights from Delhi to Mumbai",
        "Find the cheapest flights under 5000 rupees",
        "Which airlines fly to Bangalore?",
        "Show me flights with no stops",
        "What are the average prices by airline?",
        "Find flights departing in the morning",
        "Show me business class flights",
        "Which routes have the highest prices?",
        "Find flights with duration less than 2 hours",
        "Show me flights departing in the next 7 days",
        "What is the price range for economy class?",
        "Find the most expensive flight routes",
        "Show me flights from major cities",
        "Which airlines offer the best prices?",
        "Find flights with evening departures"
    ]

if __name__ == "__main__":
    create_database() 