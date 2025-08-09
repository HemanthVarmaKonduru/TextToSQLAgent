"""
Core Text-to-SQL Agent for Bikes Natural Language to SQL conversion.
Specialized for motorcycle/bike data with context-aware processing.
"""

import logging
from typing import Dict, List, Any
from openai import OpenAI
import pandas as pd

from ..config.settings import settings
from ..utils.database import DatabaseManager

logger = logging.getLogger(__name__)

class TextToSQLAgent:
    """Main agent for converting natural language to SQL queries with multi-database support."""
    
    def __init__(self, database_type: str = "airlines"):
        """
        Initialize the Text-to-SQL agent.
        
        Args:
            database_type: The database type to use ("airlines" or "bikes")
        """
        # Validate configuration
        if not settings.validate_config():
            raise ValueError("Configuration validation failed. Please check your environment variables.")
        
        # Initialize OpenAI client
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY
        )
        
        # Initialize database manager
        self.db_manager = DatabaseManager()
        
        # Set initial database context
        self.set_database_context(database_type)
        
        logger.info(f"TextToSQLAgent initialized successfully with {database_type} database")
    
    def set_database_context(self, database_type: str):
        """Set the database context for the agent."""
        if database_type not in ["airlines", "bikes"]:
            raise ValueError(f"Unsupported database type: {database_type}")
        
        self.current_database = database_type
        self.db_manager.set_current_database(database_type)
        self.schema_info = self.db_manager.get_database_schema(database_type)
        
        logger.info(f"Database context set to: {database_type}")
    
    def natural_language_to_sql(self, query: str) -> str:
        """Convert natural language query to SQL using Azure OpenAI with context-aware prompts."""
        
        if self.current_database == "airlines":
            system_prompt = self._get_airlines_system_prompt()
        elif self.current_database == "bikes":
            system_prompt = self._get_bikes_system_prompt()
        else:
            raise ValueError(f"Unsupported database type: {self.current_database}")
        
        try:
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                max_tokens=500,
                temperature=0.1
            )
            
            sql_query = response.choices[0].message.content.strip()
            
            # Check if the response is an error message
            if sql_query.startswith("ERROR:"):
                raise ValueError(sql_query)
            
            # Clean up the SQL query (remove markdown formatting if present)
            if sql_query.startswith('```sql'):
                sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
            elif sql_query.startswith('```'):
                sql_query = sql_query.replace('```', '').strip()
            
            logger.info(f"Generated SQL: {sql_query}")
            return sql_query
            
        except Exception as e:
            logger.error(f"Error converting to SQL: {e}")
            raise
    
    def _get_airlines_system_prompt(self) -> str:
        """Get system prompt for airlines database."""
        return f"""You are an expert SQL developer specialized in airlines database queries ONLY. 

CRITICAL RULES:
1. You can ONLY answer questions related to airlines, flights, cities, and travel data
2. If the user asks ANY question not related to airlines/flights data, respond with: "ERROR: This question is not related to airlines data. Please ask questions only about flights, airlines, cities, prices, routes, or travel information."
3. Do NOT answer general knowledge questions, current events, or questions outside the airlines domain
4. Only generate SQL queries for airlines-related questions

{self.schema_info}

Valid Airlines Topics:
- Flight information (routes, times, prices, duration)
- Airline comparisons and statistics
- City-to-city travel options
- Price analysis and trends
- Flight class types (Economy, Business)
- Stop information (direct vs connecting flights)
- Departure and arrival times
- Days until departure

SQL Generation Rules:
1. Only return the SQL query, no explanations
2. Use proper PostgreSQL syntax
3. Include appropriate JOINs between airlines, cities, and flights tables
4. Use meaningful column aliases for better readability
5. Add LIMIT 100 if the query might return many rows
6. Include ORDER BY when appropriate for meaningful results
7. Use LOWER() function for case-insensitive city name comparisons

Valid Airlines Query Examples:
- "Show me flights from Delhi to Mumbai" -> SELECT f.flight_id, a.airline_name, f.flight_number, sc.city_name AS source_city, dc.city_name AS destination_city, f.departure_time, f.arrival_time, f.stops, f.class_type, f.duration, f.price FROM flights f JOIN airlines a ON f.airline_id = a.airline_id JOIN cities sc ON f.source_city_id = sc.city_id JOIN cities dc ON f.destination_city_id = dc.city_id WHERE LOWER(sc.city_name) = 'delhi' AND LOWER(dc.city_name) = 'mumbai' ORDER BY f.departure_time LIMIT 100;
- "Find the cheapest flights under 5000 rupees" -> SELECT a.airline_name, f.flight_number, sc.city_name AS source_city, dc.city_name AS destination_city, f.price FROM flights f JOIN airlines a ON f.airline_id = a.airline_id JOIN cities sc ON f.source_city_id = sc.city_id JOIN cities dc ON f.destination_city_id = dc.city_id WHERE f.price < 5000 ORDER BY f.price ASC LIMIT 100;
- "Which airlines fly to Bangalore?" -> SELECT DISTINCT a.airline_name FROM flights f JOIN airlines a ON f.airline_id = a.airline_id JOIN cities dc ON f.destination_city_id = dc.city_id WHERE LOWER(dc.city_name) = 'bangalore' ORDER BY a.airline_name;

Invalid Questions (DO NOT ANSWER):
- General knowledge questions (presidents, capitals, history)
- Current events or news
- Questions about other databases or topics
- Mathematical calculations outside flight data
- Personal information or non-travel topics

If the user asks an invalid question, respond with exactly: ERROR: This question is not related to airlines data. Please ask questions only about flights, airlines, cities, prices, routes, or travel information."""
    
    def _get_bikes_system_prompt(self) -> str:
        """Get system prompt for bikes database."""
        return f"""You are an expert SQL developer specialized in motorcycle/bikes database queries ONLY.

CRITICAL RULES:
1. You can ONLY answer questions related to motorcycles, bikes, specifications, and vehicle data
2. If the user asks ANY question not related to bikes/motorcycles data, respond with: "ERROR: This question is not related to bikes data. Please ask questions only about motorcycles, specifications, performance, features, or vehicle information."
3. Do NOT answer general knowledge questions, current events, or questions outside the motorcycle domain
4. Only generate SQL queries for bike-related questions

{self.schema_info}

Valid Bikes Topics:
- Motorcycle specifications (engine, power, torque)
- Brand and model information
- Performance metrics (top speed, mileage, acceleration)
- Technical features (ABS, transmission, suspension)
- Pricing and value comparisons
- Fuel efficiency and range
- Physical dimensions (weight, height, wheelbase)
- Brake and safety systems

SQL Generation Rules:
1. Only return the SQL query, no explanations
2. Use proper PostgreSQL syntax
3. Use JOINs between bikes and bike_brands tables when needed
4. Use meaningful column aliases for better readability
5. Add LIMIT 100 if the query might return many rows
6. Include ORDER BY when appropriate for meaningful results
7. Use LOWER() and LIKE for case-insensitive text searches
8. Handle price comparisons carefully using REGEXP_REPLACE to extract numbers
9. For engine capacity searches, use LIKE with patterns like '%1000%' or '%1000cc%'
10. For top_speed/numeric comparisons, filter out '--' values: WHERE b.top_speed != '--' AND REGEXP_REPLACE(b.top_speed, '[^0-9\\.]', '', 'g') != ''
11. Remember price and numeric columns are TEXT type, so use appropriate string functions
12. If the user asks for the "fastest" bike or "highest top speed", ORDER BY CAST(NULLIF(REGEXP_REPLACE(b.top_speed, '[^0-9\\.]', '', 'g'), '') AS NUMERIC) DESC LIMIT 1, ensuring you filter out non-numeric values as in rule 10.

Valid Bikes Query Examples:
- "Show me all 1000CC bikes" -> SELECT b.bike_name, b.engine_capacity, b.max_power, b.price, b.top_speed FROM bikes b WHERE b.engine_capacity LIKE '%1000%' OR b.engine_capacity LIKE '%1000cc%' ORDER BY b.bike_name LIMIT 100;
- "Find Ducati bikes" -> SELECT b.bike_name, b.engine_capacity, b.max_power, b.price, b.top_speed FROM bikes b JOIN bike_brands br ON b.brand_id = br.brand_id WHERE LOWER(br.brand_name) = 'ducati' ORDER BY b.bike_name LIMIT 100;
- "Show bikes under 10 lakhs" -> SELECT b.bike_name, b.engine_capacity, b.price, b.max_power FROM bikes b WHERE b.price IS NOT NULL AND CAST(REGEXP_REPLACE(b.price, '[^0-9]', '', 'g') AS BIGINT) < 1000000 ORDER BY CAST(REGEXP_REPLACE(b.price, '[^0-9]', '', 'g') AS BIGINT) LIMIT 100;
- "Which bikes have disc brakes?" -> SELECT b.bike_name, b.front_brake_type, b.rear_brake_type, b.price FROM bikes b WHERE LOWER(b.front_brake_type) LIKE '%disc%' OR LOWER(b.rear_brake_type) LIKE '%disc%' ORDER BY b.bike_name LIMIT 100;
- "Show bikes with top speed over 200" -> SELECT b.bike_name, b.engine_capacity, b.top_speed, b.max_power, b.price FROM bikes b WHERE b.top_speed != '--' AND REGEXP_REPLACE(b.top_speed, '[^0-9\\.]', '', 'g') != '' AND CAST(NULLIF(REGEXP_REPLACE(b.top_speed, '[^0-9\\.]', '', 'g'), '') AS NUMERIC) > 200 ORDER BY CAST(NULLIF(REGEXP_REPLACE(b.top_speed, '[^0-9\\.]', '', 'g'), '') AS NUMERIC) DESC LIMIT 100;
- "Which is the fastest bike?" -> SELECT b.bike_name, br.brand_name, b.top_speed FROM bikes b JOIN bike_brands br ON b.brand_id = br.brand_id WHERE b.top_speed != '--' AND REGEXP_REPLACE(b.top_speed, '[^0-9\\.]', '', 'g') != '' ORDER BY CAST(NULLIF(REGEXP_REPLACE(b.top_speed, '[^0-9\\.]', '', 'g'), '') AS NUMERIC) DESC LIMIT 1;

Invalid Questions (DO NOT ANSWER):
- General knowledge questions (presidents, capitals, history)
- Current events or news
- Questions about other databases or topics
- Mathematical calculations outside bike data
- Personal information or non-vehicle topics

If the user asks an invalid question, respond with exactly: ERROR: This question is not related to bikes data. Please ask questions only about motorcycles, specifications, performance, features, or vehicle information."""
    
    def execute_sql_query(self, sql_query: str) -> pd.DataFrame:
        """Execute SQL query and return results."""
        try:
            logger.info("Executing SQL query...")
            df = self.db_manager.execute_query(sql_query)
            logger.info(f"Retrieved {len(df)} rows")
            return df
        except Exception as e:
            logger.error(f"Error executing SQL: {e}")
            raise
    
    def generate_insights(self, df: pd.DataFrame, original_query: str) -> str:
        """Generate insights from query results using Azure OpenAI."""
        
        if df.empty:
            return f"No data found for your query about {self.current_database}. Try a different search or check your criteria."
        
        # Prepare data summary
        data_summary = f"Query: {original_query}\n"
        data_summary += f"Results: {len(df)} records found\n"
        data_summary += f"Columns: {', '.join(df.columns.tolist())}\n"
        
        # Add sample data
        if len(df) > 0:
            data_summary += f"Sample data:\n{df.head(3).to_string()}\n"
        
        # Add data statistics
        if len(df) > 1:
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                data_summary += f"Numeric summary:\n{df[numeric_cols].describe().to_string()}\n"
        
        context_prompt = f"""Analyze the following {self.current_database} data and provide meaningful insights. 
Focus on patterns, trends, and key findings. Be specific and actionable.

{data_summary}

Provide a clear, concise analysis in 3-4 sentences."""
        
        try:
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": f"You are a {self.current_database} data analyst. Provide clear, actionable insights."},
                    {"role": "user", "content": context_prompt}
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            insights = response.choices[0].message.content.strip()
            logger.info("Generated insights successfully")
            return insights
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return f"Analysis complete. Found {len(df)} records matching your {self.current_database} query."
    
    def suggest_visualizations(self, df: pd.DataFrame, query: str) -> List[str]:
        """Suggest appropriate visualizations for the data."""
        
        if df.empty:
            return []
        
        suggestions = []
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        if self.current_database == "airlines":
            if 'price' in df.columns:
                suggestions.append("Price Distribution")
                if len(categorical_cols) > 0:
                    suggestions.append("Price by Category")
            
            if 'airline_name' in df.columns:
                suggestions.append("Airlines Comparison")
            
            if any(col in df.columns for col in ['source_city', 'destination_city']):
                suggestions.append("Route Analysis")
        
        elif self.current_database == "bikes":
            if 'price' in df.columns:
                suggestions.append("Price Distribution")
            
            if 'brand_name' in df.columns:
                suggestions.append("Brand Comparison")
            
            if 'mileage' in df.columns:
                suggestions.append("Mileage Analysis")
            
            if 'max_power' in df.columns or 'top_speed' in df.columns:
                suggestions.append("Performance Metrics")
        
        # Generic suggestions based on data types
        if len(numeric_cols) >= 2:
            suggestions.append("Correlation Analysis")
        
        if len(categorical_cols) > 0 and len(numeric_cols) > 0:
            suggestions.append("Category Breakdown")
        
        return suggestions[:4]  # Limit to 4 suggestions
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Process a complete natural language query and return structured results."""
        try:
            # Convert to SQL
            logger.info(f"Converting query: {query}")
            sql_query = self.natural_language_to_sql(query)
            
            # Execute query
            df = self.execute_sql_query(sql_query)
            
            # Generate insights
            logger.info("Generating insights...")
            insights = self.generate_insights(df, query)
            
            # Suggest visualizations
            logger.info("Suggesting visualizations...")
            viz_suggestions = self.suggest_visualizations(df, query)
            
            return {
                'success': True,
                'sql_query': sql_query,
                'data': df,
                'insights': insights,
                'visualizations': viz_suggestions,
                'database_type': self.current_database
            }
            
        except ValueError as e:
            # Handle non-domain questions
            error_message = str(e)
            if "not related to" in error_message:
                logger.warning(f"Non-{self.current_database} question detected: {error_message}")
                return {
                    'success': False,
                    'error_type': f'non_{self.current_database}_question',
                    'insights': error_message,
                    'sql_query': '',
                    'data': pd.DataFrame(),
                    'visualizations': [],
                    'database_type': self.current_database
                }
            else:
                logger.error(f"ValueError in process_query: {e}")
                return {
                    'success': False,
                    'error_type': 'processing_error',
                    'insights': f"Error processing your {self.current_database} query: {str(e)}",
                    'sql_query': '',
                    'data': pd.DataFrame(),
                    'visualizations': [],
                    'database_type': self.current_database
                }
        except Exception as e:
            logger.error(f"Error in process_query: {e}")
            return {
                'success': False,
                'error_type': 'general_error',
                'insights': f"An error occurred while processing your {self.current_database} query. Please try again with a different question.",
                'sql_query': '',
                'data': pd.DataFrame(),
                'visualizations': [],
                'database_type': self.current_database
            } 