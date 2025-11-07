# chatbot/cache_manager.py
"""
Simple In-Memory Cache Manager
"""
import hashlib
from typing import Dict, Any, Optional

class SimpleCacheManager:
    """A simple dictionary-based cache to avoid re-running expensive operations."""

    def __init__(self):
        """Initializes the in-memory cache."""
        self.cache: Dict[str, Dict[str, Any]] = {}
        print("✓ In-Memory Cache Manager is ready.")

    def _generate_key(self, user_prompt: str, user_id: str) -> str:
        """Generates a consistent, unique cache key."""
        normalized_prompt = ' '.join(user_prompt.lower().strip().split())
        key_string = f"{user_id}::{normalized_prompt}"
        return hashlib.md5(key_string.encode('utf-8')).hexdigest()

    def get(self, user_prompt: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves an item from the cache. Returns None on a cache miss."""
        key = self._generate_key(user_prompt, user_id)
        if key in self.cache:
            print("[Cache HIT]")
            return self.cache[key]
        print("[Cache MISS]")
        return None

    def set(self, user_prompt: str, user_id: str, value: Dict[str, Any]):
        """Adds or updates an item in the cache."""
        key = self._generate_key(user_prompt, user_id)
        if key:
            self.cache[key] = value