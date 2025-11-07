# chatbot/activity_logger.py
"""
Activity Logger for Auditing and Improvement
"""
import json
import logging
from datetime import datetime
import os
from typing import Dict, Any

class ActivityLogger:
    """Logs all user and system interactions to a structured JSON log file."""

    def __init__(self, log_file: str = "logs/activity.log"):
        """Initializes the logger."""
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        self.logger = logging.getLogger('ChatbotActivityLogger')
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.FileHandler(log_file, encoding='utf-8')
            formatter = logging.Formatter('%(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        print("✓ Activity Logger is ready.")

    def log(self, user_id: str, prompt: str, result: Dict[str, Any]):
        """Logs a structured record of a single user-chatbot interaction."""
        result_summary = {
            "success": result.get("success"),
            "response_text": result.get("response"),
            "generated_query": result.get("generated_query"),
            "intent": result.get("intent", {}).get("intent", "unknown"),
            "chart_type": result.get("chart_type", "none"),
            "error_message": result.get("error"),
            "is_from_cache": result.get("from_cache", False)
        }

        log_entry = {
            "timestamp_utc": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "user_prompt": prompt,
            "interaction_result": result_summary
        }
        
        try:
            self.logger.info(json.dumps(log_entry))
        except Exception as e:
            print(f"[ActivityLogger Error] Failed to log entry: {e}")