"""
Multi-Domain Text-to-SQL Agent Streamlit Application.
Supports Airlines and Bikes databases with natural language querying.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import logging
from auth_service import get_supabase_auth

# Import our custom modules
from src.core.text_to_sql_agent import TextToSQLAgent
from src.config.settings import settings
from src.utils.visualization import DataVisualizer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Streamlit page
st.set_page_config(
    page_title="Multi-Domain Text-to-SQL Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .database-selector {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .success-message {
        color: #0066cc;
        font-weight: bold;
    }
    .error-message {
        color: #ff0000;
        font-weight: bold;
    }
    .info-box {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .metric-container {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    .sql-editor {
        background-color: #f8f9fa;
        border: 2px solid #e9ecef;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .sql-button {
        margin: 0.5rem 0;
    }
    .query-info {
        background-color: #e8f4fd;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables."""
    if 'agent' not in st.session_state:
        st.session_state.agent = None
    if 'current_database' not in st.session_state:
        st.session_state.current_database = "airlines"
    if 'query_history' not in st.session_state:
        st.session_state.query_history = []
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

def get_agent(database_type):
    """Get or create agent for the specified database type."""
    if (st.session_state.agent is None or 
        st.session_state.current_database != database_type):
        try:
            # Get connection details from session state
            connection_details = st.session_state.get('connection_details', {})
            if connection_details:
                # Convert connection details to the format expected by TextToSQLAgent
                connection_params = {
                    'DB_HOST': connection_details.get('host', 'localhost'),
                    'DB_PORT': connection_details.get('port', 5432),
                    'DB_NAME': connection_details.get('database', ''),
                    'DB_USER': connection_details.get('user', ''),
                    'DB_PASSWORD': connection_details.get('password', '')
                }
                st.session_state.agent = TextToSQLAgent(database_type=database_type, connection_params=connection_params)
            else:
                st.session_state.agent = TextToSQLAgent(database_type=database_type)
            
            st.session_state.current_database = database_type
            logger.info(f"Initialized agent for {database_type} database")
        except Exception as e:
            st.error(f"Failed to initialize agent: {e}")
            return None
    return st.session_state.agent

def display_quick_stats(agent, database_type):
    """Display quick statistics for the selected database."""
    try:
        stats = agent.db_manager.get_quick_stats(database_type)
        if stats:
            cols = st.columns(len(stats))
            for i, (key, value) in enumerate(stats.items()):
                with cols[i]:
                    st.markdown(f"""
                    <div class="metric-container">
                        <h3>{value:,}</h3>
                        <p>{key}</p>
                    </div>
                    """, unsafe_allow_html=True)
    except Exception as e:
        logger.error(f"Error displaying stats: {e}")

def display_sample_queries(agent, database_type):
    """Display sample queries organized by difficulty level for the selected database."""
    try:
        sample_queries = agent.db_manager.get_sample_queries(database_type)
        if sample_queries and any(sample_queries.values()):
            st.subheader("💡 Sample Questions by Difficulty Level")
            
            # Create three columns for different difficulty levels
            col1, col2, col3 = st.columns(3)
            
            # Simple questions
            with col1:
                st.markdown("""
                <div style="background-color: #d4edda; padding: 1rem; border-radius: 10px; border-left: 4px solid #28a745;">
                    <h4 style="color: #155724; margin-bottom: 1rem;">🟢 Simple</h4>
                </div>
                """, unsafe_allow_html=True)
                
                for i, query in enumerate(sample_queries.get("Simple", [])):
                    if st.button(f"📝 {query}", key=f"simple_{i}", use_container_width=True):
                        st.session_state.sample_query = query
                        st.rerun()
            
            # Medium questions
            with col2:
                st.markdown("""
                <div style="background-color: #fff3cd; padding: 1rem; border-radius: 10px; border-left: 4px solid #ffc107;">
                    <h4 style="color: #856404; margin-bottom: 1rem;">🟡 Medium</h4>
                </div>
                """, unsafe_allow_html=True)
                
                for i, query in enumerate(sample_queries.get("Medium", [])):
                    if st.button(f"📝 {query}", key=f"medium_{i}", use_container_width=True):
                        st.session_state.sample_query = query
                        st.rerun()
            
            # Hard questions
            with col3:
                st.markdown("""
                <div style="background-color: #f8d7da; padding: 1rem; border-radius: 10px; border-left: 4px solid #dc3545;">
                    <h4 style="color: #721c24; margin-bottom: 1rem;">🔴 Hard</h4>
                </div>
                """, unsafe_allow_html=True)
                
                for i, query in enumerate(sample_queries.get("Hard", [])):
                    if st.button(f"📝 {query}", key=f"hard_{i}", use_container_width=True):
                        st.session_state.sample_query = query
                        st.rerun()
            
            # Add some spacing
            st.markdown("<br>", unsafe_allow_html=True)
            
    except Exception as e:
        logger.error(f"Error displaying sample queries: {e}")

def execute_custom_sql(agent, sql_query, database_type):
    """Execute a custom SQL query and display results with LLM analysis."""
    try:
        with st.spinner(f"🔍 Processing custom SQL query with AI analysis..."):
            # Process the custom SQL through the agent's pipeline
            result = agent.process_custom_sql(sql_query)
            
        if result['success']:
            # Add to SQL history
            if 'sql_history' not in st.session_state:
                st.session_state.sql_history = []
            
            st.session_state.sql_history.append({
                'sql': sql_query,
                'database': database_type,
                'timestamp': datetime.now(),
                'rows': len(result['data'])
            })
            
            # Display success message
            st.success("✅ Custom SQL query processed successfully with AI analysis!")
            
            # Display SQL query
            st.subheader("🔍 Custom SQL Query")
            st.code(result['sql_query'], language='sql')
            
            # Display results
            if not result['data'].empty:
                st.subheader("📊 Query Results")
                st.dataframe(result['data'], use_container_width=True, height=400)
                
                # Download button
                csv = result['data'].to_csv(index=False)
                st.download_button(
                    label="📥 Download Custom Results as CSV",
                    data=csv,
                    file_name=f"{database_type}_custom_query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.info(f"No data found for your custom SQL query.")
            
            # Display AI insights
            if result['insights']:
                st.subheader("🧠 AI Insights")
                st.markdown(f'<div class="info-box">{result["insights"]}</div>', 
                           unsafe_allow_html=True)
            
            # Create visualizations
            if not result['data'].empty and result['visualizations']:
                st.subheader("📈 Data Visualizations")
                create_visualizations(result['data'], result['visualizations'], database_type)
            
        else:
            # Handle errors
            st.error(f"❌ Error processing custom SQL query: {result['insights']}")
            st.info(f"📝 **Attempted Query:** `{sql_query}`")
            
    except Exception as e:
        st.error(f"❌ Error executing custom SQL query: {str(e)}")
        st.info(f"📝 **Attempted Query:** `{sql_query}`")
        logger.error(f"Error executing custom SQL: {e}")

def process_query(agent, query, database_type):
    """Process a user query and display results."""
    try:
        with st.spinner(f"🔍 Processing your {database_type} query..."):
            result = agent.process_query(query)
            
        if result['success']:
            # Initialize session state for SQL editor
            if 'original_sql_query' not in st.session_state:
                st.session_state.original_sql_query = result['sql_query']
            if 'sql_editor' not in st.session_state:
                st.session_state.sql_editor = result['sql_query']
            
            # Update session state with new query
            st.session_state.original_sql_query = result['sql_query']
            st.session_state.sql_editor = result['sql_query']
            
            # Display success message
            st.markdown(f'<div class="success-message">✅ Query processed successfully!</div>', 
                       unsafe_allow_html=True)
            
            # Display SQL query with edit capability
            with st.expander("🔍 Generated SQL Query", expanded=True):
                st.code(result['sql_query'], language='sql')
                
                # SQL Query Editor Section
                st.markdown("---")
                st.subheader("✏️ Edit & Run SQL Query")
                
                # Create a form for better UX
                with st.form("sql_editor_form"):
                    # Editable SQL query text area with default value
                    edited_sql = st.text_area(
                        "Edit the SQL query below:",
                        value=st.session_state.sql_editor,
                        height=150,
                        key="sql_editor_new",
                        help="Modify the SQL query and click 'Run Edited Query' to execute it. Press Ctrl+Enter to run quickly."
                    )
                    
                    # Form submit button (this will trigger on Enter)
                    run_edited = st.form_submit_button("🚀 Run Edited Query", type="primary", use_container_width=True)
                    
                    if run_edited:
                        # Get the current value from the text area
                        current_sql = st.session_state.sql_editor_new
                        if current_sql and current_sql.strip():
                            # Execute the edited SQL query
                            execute_custom_sql(agent, current_sql, database_type)
                        else:
                            st.error("❌ Please enter a valid SQL query.")
                
                # Additional buttons outside the form
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    if st.button("🔄 Reset to Original", key="reset_sql"):
                        st.session_state.sql_editor_new = st.session_state.original_sql_query
                        st.rerun()
                
                with col2:
                    if st.button("📋 Copy SQL", key="copy_sql"):
                        st.write("SQL copied to clipboard!")
                        st.code(st.session_state.sql_editor_new, language='sql')
            
            # Display results
            if not result['data'].empty:
                st.subheader("📊 Query Results")
                st.dataframe(result['data'], use_container_width=True, height=400)
                
                # Download button
                csv = result['data'].to_csv(index=False)
                st.download_button(
                    label="📥 Download Results as CSV",
                    data=csv,
                    file_name=f"{database_type}_query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.info(f"No data found for your {database_type} query.")
            
            # Display insights
            if result['insights']:
                st.subheader("🧠 AI Insights")
                st.markdown(f'<div class="info-box">{result["insights"]}</div>', 
                           unsafe_allow_html=True)
            
            # Create visualizations
            if not result['data'].empty and result['visualizations']:
                st.subheader("📈 Data Visualizations")
                create_visualizations(result['data'], result['visualizations'], database_type)
        
        else:
            # Handle different types of errors
            if result.get('error_type') == f'non_{database_type}_question':
                st.error(f"❌ Question Not Related to {database_type.title()} Data")
                st.markdown(f'<div class="error-message">{result["insights"]}</div>', 
                           unsafe_allow_html=True)
                
                # Provide helpful suggestions based on database type
                st.subheader("💡 Try asking questions about:")
                if database_type == "airlines":
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("""
                        **Flight Information:**
                        - Show me flights from Delhi to Mumbai
                        - Find the cheapest flights under 5000 rupees
                        - Which airlines fly to Bangalore?
                        - Show me business class flights
                        """)
                    with col2:
                        st.markdown("""
                        **Travel Analysis:**
                        - Find flights with no stops
                        - What are the average prices by airline?
                        - Show me flights departing in the morning
                        - Which routes have the highest prices?
                        """)
                elif database_type == "bikes":
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("""
                        **Bike Information:**
                        - Show me all 1000CC bikes
                        - Find all Ducati bikes
                        - Show me bikes under 10 lakhs
                        - Which bikes have the best mileage?
                        """)
                    with col2:
                        st.markdown("""
                        **Performance Analysis:**
                        - Find the most powerful bikes
                        - Show me electric bikes
                        - Which bikes have disc brakes?
                        - Find bikes by engine capacity
                        """)
            else:
                st.error("❌ Error processing query")
                st.markdown(f'<div class="error-message">{result["insights"]}</div>', 
                           unsafe_allow_html=True)
                
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        st.error(f"An unexpected error occurred: {str(e)}")

def create_visualizations(df, viz_suggestions, database_type):
    """Create visualizations based on suggestions."""
    try:
        visualizer = DataVisualizer()
        
        # Create columns for visualizations
        num_viz = min(len(viz_suggestions), 4)
        if num_viz == 1:
            cols = [st.container()]
        elif num_viz == 2:
            cols = st.columns(2)
        else:
            cols = st.columns(2)
        
        for i, viz_type in enumerate(viz_suggestions[:4]):
            with cols[i % 2]:
                try:
                    if viz_type == "Price Distribution" and 'price' in df.columns:
                        # Clean price data for visualization
                        price_col = df['price'].astype(str).str.replace('[₹,]', '', regex=True)
                        numeric_prices = pd.to_numeric(price_col, errors='coerce').dropna()
                        if not numeric_prices.empty:
                            fig = px.histogram(x=numeric_prices, 
                                             title=f"{database_type.title()} Price Distribution",
                                             labels={'x': 'Price (₹)', 'y': 'Count'})
                            st.plotly_chart(fig, use_container_width=True)
                    
                    elif viz_type == "Brand Comparison" and 'brand_name' in df.columns:
                        brand_counts = df['brand_name'].value_counts().head(10)
                        fig = px.bar(x=brand_counts.index, y=brand_counts.values,
                                   title="Bikes by Brand",
                                   labels={'x': 'Brand', 'y': 'Count'})
                        st.plotly_chart(fig, use_container_width=True)
                    
                    elif viz_type == "Airlines Comparison" and 'airline_name' in df.columns:
                        airline_counts = df['airline_name'].value_counts().head(10)
                        fig = px.bar(x=airline_counts.index, y=airline_counts.values,
                                   title="Flights by Airline",
                                   labels={'x': 'Airline', 'y': 'Count'})
                        st.plotly_chart(fig, use_container_width=True)
                    
                    elif viz_type == "Mileage Analysis" and 'mileage' in df.columns:
                        mileage_data = df['mileage'].dropna()
                        if not mileage_data.empty:
                            fig = px.histogram(x=mileage_data,
                                             title="Mileage Distribution",
                                             labels={'x': 'Mileage (km/l)', 'y': 'Count'})
                            st.plotly_chart(fig, use_container_width=True)
                    
                    elif viz_type == "Performance Metrics":
                        if 'max_power' in df.columns and 'top_speed' in df.columns:
                            # Extract numeric values from power and speed
                            power_vals = df['max_power'].astype(str).str.extract(r'(\d+\.?\d*)').astype(float)
                            speed_vals = df['top_speed'].astype(str).str.extract(r'(\d+)').astype(float)
                            
                            plot_df = pd.DataFrame({
                                'power': power_vals[0],
                                'speed': speed_vals[0],
                                'bike': df['bike_name']
                            }).dropna()
                            
                            if not plot_df.empty:
                                fig = px.scatter(plot_df, x='power', y='speed', hover_name='bike',
                                               title="Power vs Top Speed",
                                               labels={'power': 'Max Power (bhp)', 'speed': 'Top Speed (kmph)'})
                                st.plotly_chart(fig, use_container_width=True)
                
                except Exception as viz_error:
                    logger.error(f"Error creating visualization {viz_type}: {viz_error}")
                    st.warning(f"Could not create {viz_type} visualization")
    
    except Exception as e:
        logger.error(f"Error in create_visualizations: {e}")
        st.warning("Could not create visualizations")

def main():
    """Main application function."""
    # Initialize Supabase auth and check authentication
    try:
        auth = get_supabase_auth()
    except ValueError as e:
        st.error(f"❌ Configuration Error: {e}")
        return
    
    if not auth.is_authenticated():
        st.error("❌ Please log in to access the application.")
        st.info("Please run the login page first: `streamlit run login.py`")
        if st.button("🔐 Go to Login"):
            st.rerun()
        return
    
    # Check database connection
    if not st.session_state.get('connection_established', False):
        st.error("❌ Please establish database connection first.")
        st.info("Please run the database connection page: `streamlit run database_connection.py`")
        if st.button("🗄️ Go to Database Connection"):
            st.rerun()
        return
    
    # Initialize session state
    initialize_session_state()
    
    # User info and logout in sidebar
    with st.sidebar:
        st.header("👤 User Information")
        user_response = auth.get_current_user()
        if user_response["success"]:
            user = user_response["user"]
            st.write(f"**User:** {user.email}")
            st.write(f"**Auth:** Supabase")
            st.write(f"**User ID:** {user.id[:8]}...")
        
        # Database connection info
        st.header("🗄️ Database Connection")
        connection_details = st.session_state.get('connection_details', {})
        if connection_details:
            st.write(f"**Host:** {connection_details.get('host', 'N/A')}")
            st.write(f"**Database:** {connection_details.get('database', 'N/A')}")
            st.write(f"**User:** {connection_details.get('user', 'N/A')}")
            connection_time = st.session_state.get('connection_timestamp')
            if connection_time:
                st.write(f"**Connected:** {connection_time.strftime('%H:%M:%S')}")
        
        # Logout button
        if st.button("🚪 Logout", type="secondary", key="logout_btn"):
            auth.sign_out()
            # Clear all session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.success("Logged out successfully!")
            st.rerun()
        
        st.divider()
    
    # Main header
    st.markdown('<h1 class="main-header">🤖 Multi-Domain Text-to-SQL Agent</h1>', 
                unsafe_allow_html=True)
    
    # Database selector
    st.markdown('<div class="database-selector">', unsafe_allow_html=True)
    st.subheader("🗃️ Select Database")
    
    database_options = {
        "airlines": "✈️ Airlines - Flight information, routes, prices, and schedules",
        "bikes": "🏍️ Bikes - Motorcycle specifications, performance, and features"
    }
    
    selected_database = st.selectbox(
        "Choose your database:",
        options=list(database_options.keys()),
        format_func=lambda x: database_options[x],
        index=0 if st.session_state.current_database == "airlines" else 1,
        help="Select the database you want to query"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Get agent for selected database
    agent = get_agent(selected_database)
    if agent is None:
        st.error("Failed to initialize the agent. Please check your configuration.")
        return
    
    # Display database information
    st.markdown(f"**Current Database:** {selected_database.title()}")
    st.markdown(f"*{agent.db_manager.get_database_description(selected_database)}*")
    
    # Display quick stats
    st.subheader("📊 Quick Statistics")
    display_quick_stats(agent, selected_database)
    
    # Main query interface
    st.subheader(f"🔍 Ask Questions About {selected_database.title()} Data")
    
    # Check for sample query selection
    if 'sample_query' in st.session_state:
        query = st.text_area(
            "Enter your question:",
            value=st.session_state.sample_query,
            height=100,
            help=f"Ask any question about {selected_database} data in natural language"
        )
        del st.session_state.sample_query
    else:
        query = st.text_area(
            "Enter your question:",
            height=100,
            help=f"Ask any question about {selected_database} data in natural language",
            placeholder=f"e.g., Show me all {selected_database} with specific criteria..."
        )
    
    # Process query button
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("🚀 Process Query", type="primary", use_container_width=True):
            if query.strip():
                # Add to query history
                st.session_state.query_history.append({
                    'query': query,
                    'database': selected_database,
                    'timestamp': datetime.now()
                })
                
                # Process the query
                process_query(agent, query, selected_database)
            else:
                st.warning("Please enter a question first!")
    
    with col2:
        if st.button("🗑️ Clear", use_container_width=True):
            st.rerun()
    
    # Display sample queries
    display_sample_queries(agent, selected_database)
    
    # Sidebar with additional information
    with st.sidebar:
        st.header("ℹ️ Information")
        
        # Database schema
        with st.expander(f"📋 {selected_database.title()} Database Schema"):
            schema_info = agent.db_manager.get_database_schema(selected_database)
            st.text(schema_info)
        
        # Query history
        if st.session_state.query_history:
            st.subheader("📝 Recent Queries")
            recent_queries = st.session_state.query_history[-5:]  # Show last 5
            for i, item in enumerate(reversed(recent_queries)):
                with st.expander(f"{item['database'].title()}: {item['query'][:30]}..."):
                    st.write(f"**Database:** {item['database']}")
                    st.write(f"**Query:** {item['query']}")
                    st.write(f"**Time:** {item['timestamp'].strftime('%H:%M:%S')}")
        
        # SQL Query History
        if 'sql_history' not in st.session_state:
            st.session_state.sql_history = []
        
        if st.session_state.sql_history:
            st.subheader("🔧 Recent SQL Queries")
            recent_sql = st.session_state.sql_history[-3:]  # Show last 3
            for i, sql_item in enumerate(reversed(recent_sql)):
                with st.expander(f"SQL {len(recent_sql) - i}: {sql_item['sql'][:40]}..."):
                    st.code(sql_item['sql'], language='sql')
                    st.write(f"**Database:** {sql_item['database']}")
                    st.write(f"**Time:** {sql_item['timestamp'].strftime('%H:%M:%S')}")
                    st.write(f"**Rows:** {sql_item['rows']}")
        
        # Help section
        st.subheader("❓ Help")
        st.markdown("""
        **How to use:**
        1. Select your database (Airlines or Bikes)
        2. Type your question in natural language
        3. Click 'Process Query' to get results
        4. View the generated SQL, data, and insights
        
        **Tips:**
        - Be specific in your questions
        - Use sample queries as examples
        - Switch databases to explore different data
        """)

if __name__ == "__main__":
    main() 