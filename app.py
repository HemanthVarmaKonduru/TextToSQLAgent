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

def get_agent(database_type):
    """Get or create agent for the specified database type."""
    if (st.session_state.agent is None or 
        st.session_state.current_database != database_type):
        try:
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
    """Display sample queries for the selected database."""
    try:
        sample_queries = agent.db_manager.get_sample_queries(database_type)
        if sample_queries:
            st.subheader("💡 Sample Questions")
            cols = st.columns(2)
            for i, query in enumerate(sample_queries):
                col_idx = i % 2
                with cols[col_idx]:
                    if st.button(f"📝 {query}", key=f"sample_{i}"):
                        st.session_state.sample_query = query
                        st.rerun()
    except Exception as e:
        logger.error(f"Error displaying sample queries: {e}")

def process_query(agent, query, database_type):
    """Process a user query and display results."""
    try:
        with st.spinner(f"🔍 Processing your {database_type} query..."):
            result = agent.process_query(query)
            
        if result['success']:
            # Display success message
            st.markdown(f'<div class="success-message">✅ Query processed successfully!</div>', 
                       unsafe_allow_html=True)
            
            # Display SQL query
            with st.expander("🔍 Generated SQL Query", expanded=False):
                st.code(result['sql_query'], language='sql')
            
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
    # Initialize session state
    initialize_session_state()
    
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