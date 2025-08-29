import os
import logging
from datetime import datetime
from supabase import create_client, Client
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class UserTracker:
    def __init__(self):
        """Initialize Supabase client for user tracking"""
        self.supabase: Optional[Client] = None
        self.setup_supabase()
    
    def setup_supabase(self):
        """Setup Supabase connection"""
        try:
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_ANON_KEY")
            
            if not supabase_url or not supabase_key:
                logger.warning("Supabase credentials not found. User tracking will be disabled.")
                return
            
            self.supabase = create_client(supabase_url, supabase_key)
            logger.info("Supabase client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            self.supabase = None
    
    def track_user(self, user_id: int, username: str = None, first_name: str = None, last_name: str = None) -> bool:
        """Track a new user or update existing user"""
        if not self.supabase:
            logger.warning("Supabase not available, skipping user tracking")
            return False
        
        try:
            # Check if user already exists
            response = self.supabase.table("users").select("*").eq("telegram_id", user_id).execute()
            
            if response.data:
                # Update existing user
                self.supabase.table("users").update({
                    "last_seen": datetime.utcnow().isoformat(),
                    "username": username,
                    "first_name": first_name,
                    "last_name": last_name
                }).eq("telegram_id", user_id).execute()
                logger.info(f"Updated user {user_id}")
            else:
                # Create new user
                self.supabase.table("users").insert({
                    "telegram_id": user_id,
                    "username": username,
                    "first_name": first_name,
                    "last_name": last_name,
                    "first_seen": datetime.utcnow().isoformat(),
                    "last_seen": datetime.utcnow().isoformat(),
                    "message_count": 0
                }).execute()
                logger.info(f"Created new user {user_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to track user {user_id}: {e}")
            return False
    
    def increment_message_count(self, user_id: int) -> bool:
        """Increment message count for a user"""
        if not self.supabase:
            return False
        
        try:
            # Get current message count
            response = self.supabase.table("users").select("message_count").eq("telegram_id", user_id).execute()
            if response.data:
                current_count = response.data[0].get("message_count", 0)
                new_count = current_count + 1
                
                # Update with new count
                self.supabase.table("users").update({
                    "message_count": new_count,
                    "last_seen": datetime.utcnow().isoformat()
                }).eq("telegram_id", user_id).execute()
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to increment message count for user {user_id}: {e}")
            return False
    
    def get_user_count(self) -> int:
        """Get total number of users"""
        if not self.supabase:
            return 0
        
        try:
            response = self.supabase.table("users").select("*").execute()
            return len(response.data) if response.data else 0
        except Exception as e:
            logger.error(f"Failed to get user count: {e}")
            return 0
    
    def get_active_users_today(self) -> int:
        """Get number of users active today"""
        if not self.supabase:
            return 0
        
        try:
            today = datetime.utcnow().date().isoformat()
            response = self.supabase.table("users").select("*").gte("last_seen", today).execute()
            return len(response.data) if response.data else 0
        except Exception as e:
            logger.error(f"Failed to get active users count: {e}")
            return 0
