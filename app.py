"""
Main Streamlit application for the Airlines Text-to-SQL Agent.
Uses the clean, modular structure with proper configuration management.
"""

import streamlit as st
import time
import pandas as pd
from typing import Dict, Any

# Import from our clean structure
from src.core import TextToSQLAgent
from src.config import settings
from src.utils import DataVisualizer

# Page configuration
st.set_page_config(
    page_title=settings.STREAMLIT_TITLE,
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .error-message {
        background-color: #ffebee;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #f44336;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #e8f5e8;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #4caf50;
        margin: 1rem 0;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main application function."""
    
    # Header
    st.markdown(f'<h1 class="main-header">{settings.STREAMLIT_TITLE}</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-header">{settings.STREAMLIT_DESCRIPTION}</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("📊 Database Schema")
        st.markdown("""
        **airlines** table:
        - airline_id, airline_name, airline_code
        
        **cities** table:
        - city_id, city_name, country
        
        **flights** table:
        - flight_id, airline_id, flight_number, source_city_id, destination_city_id
        - departure_time, arrival_time, stops, class_type, duration, price
        """)
        
        st.header("💡 Example Queries")
        example_queries = [
            "Show me flights from Delhi to Mumbai",
            "Find the cheapest flights under 5000 rupees",
            "Which airlines fly to Bangalore?",
            "Show me business class flights",
            "Find flights with no stops",
            "What are the average prices by airline?",
            "Show me flights departing in the morning",
            "Which routes have the highest prices?"
        ]
        
        for query in example_queries:
            if st.button(query, key=f"example_{query}"):
                st.session_state.user_query = query
        
        st.header("📈 Quick Stats")
        try:
            agent = TextToSQLAgent()
            db_manager = agent.db_manager
            
            # Get some quick stats
            total_flights = len(db_manager.execute_query("SELECT COUNT(*) as count FROM flights"))
            avg_price = db_manager.execute_query("SELECT AVG(price) as avg_price FROM flights")
            airlines_count = len(db_manager.execute_query("SELECT COUNT(*) as count FROM airlines"))
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Flights", f"{total_flights.iloc[0]['count']:,}")
            with col2:
                st.metric("Avg Price", f"₹{avg_price.iloc[0]['avg_price']:.0f}")
            with col3:
                st.metric("Airlines", airlines_count.iloc[0]['count'])
                
        except Exception as e:
            st.error(f"Error loading stats: {e}")
    
    # Main content
    st.header("🤖 Ask About Airlines Data")
    
    # Query input
    user_query = st.text_area(
        "Enter your question about airlines data:",
        placeholder="e.g., Show me flights from Delhi to Mumbai",
        key="user_query",
        height=100
    )
    
    # Process button
    if st.button("🚀 Process Query", type="primary"):
        if user_query.strip():
            process_query(user_query)
        else:
            st.warning("Please enter a query.")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            <p>✈️ Airlines Text-to-SQL Agent | Powered by Azure OpenAI GPT-4.1 | PostgreSQL Database</p>
        </div>
        """,
        unsafe_allow_html=True
    )

def process_query(user_query: str):
    """Process the user query and display results."""
    
    # Progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Initialize agent
        status_text.text("Initializing agent...")
        progress_bar.progress(20)
        
        agent = TextToSQLAgent()
        
        # Process query
        status_text.text("Processing your query...")
        progress_bar.progress(50)
        
        result = agent.process_query(user_query)
        progress_bar.progress(100)
        
        # Display results
        if result['success']:
            st.success("✅ Query processed successfully!")
            
            # Display SQL query
            st.subheader("🔍 Generated SQL Query")
            st.code(result['sql_query'], language='sql')
            
            # Display data
            st.subheader("📊 Query Results")
            
            # Show data info
            col_data1, col_data2, col_data3 = st.columns(3)
            with col_data1:
                st.metric("Rows", len(result['data']))
            with col_data2:
                st.metric("Columns", len(result['data'].columns))
            with col_data3:
                st.metric("Memory Usage", f"{result['data'].memory_usage(deep=True).sum() / 1024:.1f} KB")
            
            # Display the data
            st.dataframe(result['data'], use_container_width=True)
            
            # Download button for data
            csv = result['data'].to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"airlines_query_results_{int(time.time())}.csv",
                mime="text/csv"
            )
            
            # Display insights
            st.subheader("🧠 AI-Generated Insights")
            st.markdown(f'<div class="info-box">{result["insights"]}</div>', unsafe_allow_html=True)
            
            # Display visualizations
            st.subheader("📈 Visualizations")
            
            if result['data'].empty:
                st.warning("No data to visualize.")
            else:
                # Create visualizations
                visualizations = DataVisualizer.auto_create_visualizations(
                    result['data'], 
                    user_query, 
                    result['visualization_suggestions']
                )
                
                if visualizations:
                    # Display each visualization
                    for viz_name, fig in visualizations.items():
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Add download button for each chart
                        col_viz1, col_viz2 = st.columns([3, 1])
                        with col_viz2:
                            if st.button(f"📥 Download {viz_name.replace('_', ' ').title()}", key=f"download_{viz_name}"):
                                # Save as PNG
                                fig.write_image(f"{viz_name}_{int(time.time())}.png")
                                st.success(f"Chart saved as {viz_name}_{int(time.time())}.png")
                else:
                    st.info("No suitable visualizations could be created for this data.")
        
        else:
            # Handle different types of errors
            if result.get('error_type') == 'non_airlines_question':
                st.error("❌ Question Not Related to Airlines Data")
                st.markdown(f'<div class="error-message">{result["insights"]}</div>', unsafe_allow_html=True)
                
                # Provide helpful suggestions
                st.subheader("💡 Try asking questions about:")
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
            else:
                st.error("❌ Error processing query")
                st.markdown(f'<div class="error-message">{result["insights"]}</div>', unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.info("Please check your configuration and database connection.")
    
    finally:
        # Clear progress
        progress_bar.empty()
        status_text.empty()

if __name__ == "__main__":
    main() 