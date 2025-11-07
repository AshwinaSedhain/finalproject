# chatbot/supabase_manager.py
"""
Supabase Manager for Persistent Chat History and Feedback
"""
import os
from typing import List, Dict, Any, Optional
from supabase import create_client, Client

class SupabaseManager:
    """Handles all communication with Supabase for chat history and feedback."""

    def __init__(self):
        url: str = os.environ.get("SUPABASE_URL")
        key: str = os.environ.get("SUPABASE_KEY")
        if not url or not key:
            raise ValueError("Supabase URL and Key must be set in your .env file.")
        try:
            self.supabase: Client = create_client(url, key)
            print(" Supabase Manager is ready and connected.")
        except Exception as e:
            print(f"Failed to connect to Supabase: {e}")
            self.supabase = None
    
    def get_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieves the most recent conversation history for a user."""
        if not self.supabase: return []
        try:
            response = self.supabase.table("chat_history").select("role", "content").eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
            return list(reversed(response.data))
        except Exception as e:
            print(f"[Supabase Error] Failed to get history for user {user_id}: {e}")
            return []

    def add_to_history(self, user_id: str, user_message: str, ai_message: str):
        """Adds a new turn (user and AI message) to the chat history."""
        if not self.supabase: return
        try:
            messages_to_insert = [
                {"user_id": user_id, "role": "user", "content": user_message},
                {"user_id": user_id, "role": "assistant", "content": ai_message},
            ]
            self.supabase.table("chat_history").insert(messages_to_insert).execute()
        except Exception as e:
            print(f"[Supabase Error] Failed to add to history for user {user_id}: {e}")

    def log_feedback(self, user_id: str, rating: str, last_interaction: Dict[str, Any]):
        """Logs user feedback (good/bad) to the feedback table."""
        if not self.supabase: return
        try:
            self.supabase.table("feedback").insert({
                "user_id": user_id,
                "rating": rating,
                "original_prompt": last_interaction.get("prompt"),
                "ai_response": last_interaction.get("response"),
                "generated_query": last_interaction.get("query")
            }).execute()
            print(f"✓ Feedback ('{rating}') logged successfully.")
        except Exception as e:
            print(f"[Supabase Error] Failed to log feedback for user {user_id}: {e}")