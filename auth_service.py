"""
Supabase Authentication Module for Text-to-SQL Agent
Handles user authentication using Supabase Auth.
"""

import os
import streamlit as st
from supabase import create_client, Client
import logging

logger = logging.getLogger(__name__)

class SupabaseAuth:
    """Handles Supabase authentication operations."""
    
    def __init__(self):
        """Initialize Supabase client."""
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.anon_key = os.getenv("ANON_KEY")
        
        if not self.supabase_url or not self.anon_key:
            raise ValueError("SUPABASE_URL and ANON_KEY environment variables are required")
        
        self.supabase: Client = create_client(self.supabase_url, self.anon_key)
    
    def sign_up(self, email: str, password: str) -> dict:
        """
        Sign up a new user.
        
        Args:
            email: User's email
            password: User's password
            
        Returns:
            dict: Response from Supabase with user data or error
        """
        try:
            response = self.supabase.auth.sign_up({
                "email": email,
                "password": password
            })
            
            if response.user:
                logger.info(f"User signed up successfully: {email}")
                return {
                    "success": True,
                    "user": response.user,
                    "message": "Sign up successful! Please check your email for verification."
                }
            else:
                return {
                    "success": False,
                    "error": "Sign up failed. Please try again."
                }
                
        except Exception as e:
            logger.error(f"Sign up error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def sign_in(self, email: str, password: str) -> dict:
        """
        Sign in an existing user.
        
        Args:
            email: User's email
            password: User's password
            
        Returns:
            dict: Response from Supabase with user data or error
        """
        try:
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user and response.session:
                logger.info(f"User signed in successfully: {email}")
                return {
                    "success": True,
                    "user": response.user,
                    "session": response.session,
                    "message": "Sign in successful!"
                }
            else:
                return {
                    "success": False,
                    "error": "Invalid email or password."
                }
                
        except Exception as e:
            logger.error(f"Sign in error: {e}")
            return {
                "success": False,
                "error": "Invalid email or password."
            }
    
    def sign_in_with_google(self) -> dict:
        """
        Sign in with Google OAuth.
        
        Returns:
            dict: Response with OAuth URL or error
        """
        try:
            response = self.supabase.auth.sign_in_with_oauth({
                "provider": "google",
                "options": {
                    "redirect_to": "http://localhost:8501"  # Adjust based on your app URL
                }
            })
            
            return {
                "success": True,
                "oauth_url": response.url if hasattr(response, 'url') else "",
                "message": "Redirecting to Google..."
            }
            
        except Exception as e:
            logger.error(f"Google OAuth error: {e}")
            return {
                "success": False,
                "error": "Google sign in failed. Please try again."
            }
    
    def sign_out(self) -> dict:
        """
        Sign out the current user.
        
        Returns:
            dict: Response indicating success or failure
        """
        try:
            response = self.supabase.auth.sign_out()
            logger.info("User signed out successfully")
            return {
                "success": True,
                "message": "Signed out successfully!"
            }
            
        except Exception as e:
            logger.error(f"Sign out error: {e}")
            return {
                "success": False,
                "error": "Sign out failed."
            }
    
    def get_current_user(self) -> dict:
        """
        Get the current authenticated user.
        
        Returns:
            dict: User data or None if not authenticated
        """
        try:
            user = self.supabase.auth.get_user()
            if user and user.user:
                return {
                    "success": True,
                    "user": user.user
                }
            else:
                return {
                    "success": False,
                    "user": None
                }
                
        except Exception as e:
            logger.error(f"Get user error: {e}")
            return {
                "success": False,
                "user": None
            }
    
    def is_authenticated(self) -> bool:
        """
        Check if user is currently authenticated.
        
        Returns:
            bool: True if authenticated, False otherwise
        """
        user_response = self.get_current_user()
        return user_response["success"] and user_response["user"] is not None

# Singleton instance
_supabase_auth = None

def get_supabase_auth() -> SupabaseAuth:
    """Get singleton instance of SupabaseAuth."""
    global _supabase_auth
    if _supabase_auth is None:
        _supabase_auth = SupabaseAuth()
    return _supabase_auth
