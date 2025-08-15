"""
Supabase Authentication Login Page for Text-to-SQL Agent
"""

import streamlit as st
import os
import sys
from auth_service import get_supabase_auth

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Main login function."""
    
    # Configure Streamlit page
    st.set_page_config(
        page_title="Login - Text-to-SQL Agent",
        page_icon="🔐",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    
    # Initialize Supabase auth
    try:
        auth = get_supabase_auth()
    except ValueError as e:
        st.error(f"❌ Configuration Error: {e}")
        st.info("Please set SUPABASE_URL and ANON_KEY environment variables.")
        return
    
    # Custom CSS for login styling
    st.markdown("""
    <style>
        .login-container {
            background-color: #f8f9fa;
            padding: 2rem;
            border-radius: 15px;
            border: 2px solid #e9ecef;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            max-width: 400px;
            margin: 0 auto;
        }
        .login-header {
            text-align: center;
            margin-bottom: 2rem;
            color: #1f77b4;
            font-size: 2rem;
            font-weight: bold;
        }
        .google-btn {
            background-color: #4285f4;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            width: 100%;
            margin-top: 1rem;
        }
        .divider {
            text-align: center;
            margin: 1rem 0;
            color: #6c757d;
        }
        .form-group {
            margin-bottom: 1rem;
        }
        .form-label {
            font-weight: bold;
            color: #495057;
            margin-bottom: 0.5rem;
        }
        .login-btn {
            background-color: #007bff;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            width: 100%;
            margin-top: 1rem;
        }
        .login-btn:hover {
            background-color: #0056b3;
        }
        .footer {
            text-align: center;
            margin-top: 2rem;
            color: #6c757d;
            font-size: 0.9rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Check if user is already authenticated
    if auth.is_authenticated():
        # Store authentication in session state and redirect
        st.session_state.authenticated = True
        user_response = auth.get_current_user()
        if user_response["success"]:
            st.session_state.user = user_response["user"]
            st.session_state.username = user_response["user"].email
        
        # Import and run the database connection page
        import database_connection
        database_connection.main()
        return
    
    # Initialize session state for authentication
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    # Login page content
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="login-header">🔐 Login</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #6c757d;">Welcome to Text-to-SQL Agent</p>', unsafe_allow_html=True)
    
    # Login form
    with st.form("login_form"):
        st.markdown('<div class="form-group">', unsafe_allow_html=True)
        st.markdown('<label class="form-label">Email</label>', unsafe_allow_html=True)
        email = st.text_input("Email", placeholder="Enter your email", key="email_input", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="form-group">', unsafe_allow_html=True)
        st.markdown('<label class="form-label">Password</label>', unsafe_allow_html=True)
        password = st.text_input("Password", type="password", placeholder="Enter your password", key="password_input", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Login and Sign Up buttons
        col1, col2 = st.columns(2)
        
        with col1:
            login_submitted = st.form_submit_button("🔑 Login", use_container_width=True)
        
        with col2:
            signup_submitted = st.form_submit_button("📝 Sign Up", use_container_width=True)
        
        if login_submitted:
            if email and password:
                with st.spinner("Signing in..."):
                    result = auth.sign_in(email, password)
                
                if result["success"]:
                    st.session_state.authenticated = True
                    st.session_state.user = result["user"]
                    st.session_state.username = result["user"].email
                    st.success("✅ Login successful! Redirecting...")
                    st.rerun()
                else:
                    st.error(f"❌ {result['error']}")
            else:
                st.error("❌ Please enter both email and password.")
        
        if signup_submitted:
            if email and password:
                with st.spinner("Creating account..."):
                    result = auth.sign_up(email, password)
                
                if result["success"]:
                    st.success("✅ Account created! Please check your email for verification.")
                    st.info("After verification, you can login with your credentials.")
                else:
                    st.error(f"❌ {result['error']}")
            else:
                st.error("❌ Please enter both email and password.")
    
    # Divider
    st.markdown('<div class="divider">OR</div>', unsafe_allow_html=True)
    
    # Google login button
    if st.button("🔍 Continue with Google", use_container_width=True, key="google_login_btn"):
        with st.spinner("Redirecting to Google..."):
            result = auth.sign_in_with_google()
        
        if result["success"]:
            st.info("Redirecting to Google for authentication...")
            # In a real app, you'd redirect to the OAuth URL
            # For now, show the URL (you'll need to handle this properly)
            st.write(f"OAuth URL: {result['oauth_url']}")
            st.info("⚠️ Note: Google OAuth requires proper redirect configuration in production.")
        else:
            st.error(f"❌ {result['error']}")
    
    # Footer
    st.markdown('<div class="footer">', unsafe_allow_html=True)
    st.markdown('<p>Powered by Supabase Authentication</p>', unsafe_allow_html=True)
    st.markdown('<p>© 2024 Text-to-SQL Agent</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Add some spacing
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Supabase auth info
    with st.expander("ℹ️ Authentication Information", expanded=False):
        st.markdown("""
        **Supabase Authentication**
        
        This application uses Supabase for secure authentication:
        
        **Sign Up:**
        - Create a new account with email and password
        - Email verification is required for new accounts
        - Check your email after signing up
        
        **Login:**
        - Use your registered email and password
        - Secure JWT-based authentication
        - Session management handled automatically
        
        **Google OAuth:**
        - Alternative login method
        - Requires proper OAuth configuration
        - Secure third-party authentication
        
        **Security:**
        - All passwords are securely hashed
        - JWT tokens for session management
        - Industry-standard security practices
        """)

if __name__ == "__main__":
    main()
