"""
Database Connection Page for Text-to-SQL Agent
Handles PostgreSQL connection setup after Supabase authentication.
"""

import streamlit as st
import os
import sys
import psycopg2
from datetime import datetime
from auth_service import get_supabase_auth

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_connection(connection_params):
    """Test the database connection with provided parameters."""
    try:
        conn = psycopg2.connect(
            host=connection_params['host'],
            port=connection_params['port'],
            database=connection_params['database'],
            user=connection_params['user'],
            password=connection_params['password']
        )
        conn.close()
        return True, "Connection successful!"
    except Exception as e:
        return False, f"Connection failed: {str(e)}"

def main():
    """Main database connection function."""
    
    # Configure Streamlit page
    st.set_page_config(
        page_title="Database Connection - Text-to-SQL Agent",
        page_icon="🗄️",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    
    # Initialize Supabase auth and check authentication
    try:
        auth = get_supabase_auth()
    except ValueError as e:
        st.error(f"❌ Configuration Error: {e}")
        return
    
    if not auth.is_authenticated():
        st.error("❌ Please log in first.")
        st.info("Please run the login page: `streamlit run login.py`")
        if st.button("🔐 Go to Login"):
            st.rerun()
        return
    
    # Custom CSS for connection page styling
    st.markdown("""
    <style>
        .connection-container {
            background-color: #f8f9fa;
            padding: 2rem;
            border-radius: 15px;
            border: 2px solid #e9ecef;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            max-width: 600px;
            margin: 0 auto;
        }
        .connection-header {
            text-align: center;
            margin-bottom: 2rem;
            color: #1f77b4;
            font-size: 2rem;
            font-weight: bold;
        }
        .form-group {
            margin-bottom: 1.5rem;
        }
        .form-label {
            font-weight: bold;
            color: #495057;
            margin-bottom: 0.5rem;
        }
        .connection-btn {
            background-color: #28a745;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 5px;
            cursor: pointer;
            width: 100%;
            margin-top: 1rem;
            font-weight: bold;
        }
        .test-btn {
            background-color: #17a2b8;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 5px;
            cursor: pointer;
            margin-top: 0.5rem;
        }
        .success-message {
            color: #28a745;
            font-weight: bold;
            padding: 1rem;
            background-color: #d4edda;
            border-radius: 5px;
            border: 1px solid #c3e6cb;
        }
        .error-message {
            color: #dc3545;
            font-weight: bold;
            padding: 1rem;
            background-color: #f8d7da;
            border-radius: 5px;
            border: 1px solid #f5c6cb;
        }
        .info-box {
            background-color: #e8f4fd;
            padding: 1rem;
            border-radius: 5px;
            border-left: 4px solid #1f77b4;
            margin: 1rem 0;
        }
        .user-info {
            background-color: #e9ecef;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            margin-bottom: 1rem;
            text-align: center;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state for connection
    if 'connection_established' not in st.session_state:
        st.session_state.connection_established = False
    if 'connection_details' not in st.session_state:
        st.session_state.connection_details = {}
    
    # If connection is already established, redirect to main app
    if st.session_state.connection_established:
        import app
        app.main()
        return
    
    # Connection page content
    st.markdown('<div class="connection-container">', unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="connection-header">🗄️ Database Connection</h1>', unsafe_allow_html=True)
    
    # Get current user info
    user_response = auth.get_current_user()
    if user_response["success"]:
        user = user_response["user"]
        username = user.email
        st.markdown(f'''
        <div class="user-info">
            <strong>👤 Logged in as:</strong> {username}
        </div>
        ''', unsafe_allow_html=True)
    
    # Logout option in top right
    col1, col2, col3 = st.columns([2, 1, 1])
    with col3:
        if st.button("🚪 Logout", type="secondary", key="logout_header"):
            auth.sign_out()
            # Clear session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.success("Logged out successfully!")
            st.rerun()
    
    # Connection form
    with st.form("connection_form"):
        st.markdown('<div class="form-group">', unsafe_allow_html=True)
        st.markdown('<label class="form-label">Host</label>', unsafe_allow_html=True)
        host = st.text_input("Host", value="localhost", placeholder="localhost", key="host_input", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="form-group">', unsafe_allow_html=True)
        st.markdown('<label class="form-label">Port</label>', unsafe_allow_html=True)
        port = st.number_input("Port", value=5432, min_value=1, max_value=65535, key="port_input", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="form-group">', unsafe_allow_html=True)
        st.markdown('<label class="form-label">Database Name</label>', unsafe_allow_html=True)
        database = st.text_input("Database", placeholder="your_database_name", key="database_input", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="form-group">', unsafe_allow_html=True)
        st.markdown('<label class="form-label">Username</label>', unsafe_allow_html=True)
        db_user = st.text_input("Username", placeholder="your_username", key="db_user_input", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="form-group">', unsafe_allow_html=True)
        st.markdown('<label class="form-label">Password</label>', unsafe_allow_html=True)
        password = st.text_input("Password", type="password", placeholder="your_password", key="db_password_input", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Test connection button
        test_connection_clicked = st.form_submit_button("🧪 Test Connection", use_container_width=True)
        
        # Connect button
        connect_clicked = st.form_submit_button("🔗 Connect to Database", use_container_width=True)
        
        if test_connection_clicked:
            if host and database and db_user and password:
                connection_params = {
                    'host': host,
                    'port': port,
                    'database': database,
                    'user': db_user,
                    'password': password
                }
                
                success, message = test_connection(connection_params)
                if success:
                    st.success(f"✅ {message}")
                else:
                    st.error(f"❌ {message}")
            else:
                st.error("❌ Please fill in all required fields.")
        
        if connect_clicked:
            if host and database and db_user and password:
                connection_params = {
                    'host': host,
                    'port': port,
                    'database': database,
                    'user': db_user,
                    'password': password
                }
                
                success, message = test_connection(connection_params)
                if success:
                    # Store connection details in session state
                    st.session_state.connection_details = connection_params
                    st.session_state.connection_established = True
                    st.session_state.connection_timestamp = datetime.now()
                    
                    st.success("✅ Database connected successfully! Redirecting to main application...")
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
            else:
                st.error("❌ Please fill in all required fields.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Add some spacing
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Help information
    with st.expander("ℹ️ Connection Help", expanded=False):
        st.markdown("""
        **PostgreSQL Connection Details:**
        
        **Host:** Usually `localhost` for local databases or your server IP
        **Port:** Default PostgreSQL port is `5432`
        **Database:** The name of your PostgreSQL database
        **Username:** Your PostgreSQL username
        **Password:** Your PostgreSQL password
        
        **Common Issues:**
        - Make sure PostgreSQL is running
        - Check if the database exists
        - Verify username and password
        - Ensure the user has proper permissions
        
        **Test Connection:** Use this to verify your credentials before connecting
        **Connect:** Establishes the connection and redirects to the main application
        """)
    
    # Logout option
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🚪 Logout", type="secondary"):
            # Clear all session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.success("Logged out successfully!")
            st.rerun()

if __name__ == "__main__":
    main()
