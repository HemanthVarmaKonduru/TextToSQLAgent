"""
Core Text-to-SQL Agent for Airlines Data.
Converts natural language queries to SQL and provides insights.
"""

import logging
import pandas as pd
import psycopg2
from openai import AzureOpenAI
from typing import Dict, Any, List, Optional

from ..config.settings import settings
from ..utils.database import DatabaseManager
from ..utils.visualization import DataVisualizer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextToSQLAgent:
    """
    Main agent class for converting natural language to SQL queries
    and providing insights on airlines data.
    """
    
    def __init__(self):
        """Initialize the Text-to-SQL agent with Azure OpenAI client."""
        try:
            # Validate configuration
            settings.validate_config()
            
            # Initialize Azure OpenAI client
            self.client = AzureOpenAI(
                api_version=settings.AZURE_OPENAI_API_VERSION,
                azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
                api_key=settings.AZURE_OPENAI_API_KEY,
            )
            
            # Initialize database manager
            self.db_manager = DatabaseManager()
            
            # Get database schema information
            self.schema_info = self.db_manager.get_database_schema()
            
            logger.info("TextToSQLAgent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize TextToSQLAgent: {e}")
            raise
    
    def natural_language_to_sql(self, user_query: str) -> str:
        """
        Convert natural language query to SQL using Azure OpenAI.
        
        Args:
            user_query: Natural language query from user
            
        Returns:
            Generated SQL query
            
        Raises:
            ValueError: If query is not related to airlines data
        """
        
        system_prompt = f"""You are an expert SQL developer specialized in airlines database queries ONLY. 

CRITICAL RULES:
1. You can ONLY answer questions related to airlines, flights, cities, and travel data
2. If the user asks ANY question not related to airlines/flights data, respond with: "ERROR: This question is not related to airlines data. Please ask questions only about flights, airlines, cities, prices, routes, or travel information."
3. Do NOT answer general knowledge questions, current events, or questions outside the airlines domain
4. Only generate SQL queries for airlines-related questions

Database Schema (Airlines Data Only):
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

        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                max_tokens=1000,
                temperature=0.1,
                model=settings.AZURE_OPENAI_DEPLOYMENT_NAME
            )
            
            sql_query = response.choices[0].message.content.strip()
            
            # Check if the response is an error message
            if sql_query.startswith("ERROR:"):
                raise ValueError(sql_query)
            
            # Clean up the SQL query (remove markdown formatting if present)
            if sql_query.startswith('```sql'):
                sql_query = sql_query[6:]
            if sql_query.endswith('```'):
                sql_query = sql_query[:-3]
            
            return sql_query.strip()
            
        except Exception as e:
            logger.error(f"Error converting to SQL: {e}")
            raise
    
    def execute_sql_query(self, sql_query: str) -> pd.DataFrame:
        """
        Execute SQL query and return results as DataFrame.
        
        Args:
            sql_query: SQL query to execute
            
        Returns:
            DataFrame with query results
        """
        return self.db_manager.execute_query(sql_query)
    
    def generate_insights(self, df: pd.DataFrame, original_query: str) -> str:
        """
        Generate insights from the data using Azure OpenAI.
        
        Args:
            df: DataFrame with query results
            original_query: Original user query
            
        Returns:
            Generated insights text
        """
        
        if df.empty:
            return "No data found for the given query."
        
        # Create a summary of the data
        data_summary = f"""
Data Summary:
- Number of rows: {len(df)}
- Number of columns: {len(df.columns)}
- Columns: {', '.join(df.columns)}
- First few rows:
{df.head().to_string()}
"""
        
        system_prompt = """You are a data analyst expert. Analyze the provided data and generate meaningful insights. 
        Focus on patterns, trends, and actionable insights. Be concise but informative."""
        
        user_prompt = f"""
Original Query: {original_query}

{data_summary}

Please provide:
1. A brief summary of what the data shows
2. Key insights and patterns
3. Any notable trends or outliers
4. Recommendations based on the data

Keep the response concise and focused on business value.
"""
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1000,
                temperature=0.7,
                model=settings.AZURE_OPENAI_DEPLOYMENT_NAME
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return "Unable to generate insights at this time."
    
    def suggest_visualizations(self, df: pd.DataFrame, original_query: str) -> List[str]:
        """
        Suggest appropriate visualizations for the data.
        
        Args:
            df: DataFrame with query results
            original_query: Original user query
            
        Returns:
            List of suggested visualization types
        """
        
        if df.empty:
            return []
        
        data_summary = f"""
Data Summary:
- Number of rows: {len(df)}
- Number of columns: {len(df.columns)}
- Columns: {', '.join(df.columns)}
- Data types: {dict(df.dtypes)}
"""
        
        system_prompt = """You are a data visualization expert. Based on the data and query, suggest the most appropriate visualization types. 
        Return only the visualization types, one per line, such as: bar_chart, line_chart, pie_chart, scatter_plot, heatmap, etc."""
        
        user_prompt = f"""
Original Query: {original_query}

{data_summary}

Suggest 2-3 most appropriate visualization types for this data.
"""
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=200,
                temperature=0.3,
                model=settings.AZURE_OPENAI_DEPLOYMENT_NAME
            )
            
            suggestions = response.choices[0].message.content.strip().split('\n')
            return [s.strip() for s in suggestions if s.strip()]
            
        except Exception as e:
            logger.error(f"Error suggesting visualizations: {e}")
            return []
    
    def process_query(self, user_query: str) -> Dict[str, Any]:
        """
        Main method to process a natural language query end-to-end.
        
        Args:
            user_query: Natural language query from user
            
        Returns:
            Dictionary with results including SQL, data, insights, and visualizations
        """
        
        try:
            # Step 1: Convert natural language to SQL
            logger.info(f"Converting query: {user_query}")
            sql_query = self.natural_language_to_sql(user_query)
            logger.info(f"Generated SQL: {sql_query}")
            
            # Step 2: Execute SQL query
            logger.info("Executing SQL query...")
            df = self.execute_sql_query(sql_query)
            logger.info(f"Retrieved {len(df)} rows")
            
            # Step 3: Generate insights
            logger.info("Generating insights...")
            insights = self.generate_insights(df, user_query)
            
            # Step 4: Suggest visualizations
            logger.info("Suggesting visualizations...")
            viz_suggestions = self.suggest_visualizations(df, user_query)
            
            return {
                'sql_query': sql_query,
                'data': df,
                'insights': insights,
                'visualization_suggestions': viz_suggestions,
                'success': True
            }
            
        except ValueError as e:
            # Handle non-airlines questions
            error_message = str(e)
            logger.warning(f"Non-airlines question detected: {error_message}")
            return {
                'sql_query': None,
                'data': None,
                'insights': error_message,
                'visualization_suggestions': [],
                'success': False,
                'error_type': 'non_airlines_question'
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                'sql_query': None,
                'data': None,
                'insights': f"Error: {str(e)}",
                'visualization_suggestions': [],
                'success': False,
                'error_type': 'general_error'
            } 