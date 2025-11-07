# chatbot/intent_classifier.py
"""
Intent Classification Module
"""
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import Dict
import warnings

warnings.filterwarnings('ignore')

class IntentClassifier:
    """
    Classifies the user's primary intent from their prompt.
    This class no longer performs domain detection.
    """

    def __init__(self):
        """Initializes the intent classification model and definitions."""
        # Load a powerful sentence transformer model for semantic understanding
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            raise RuntimeError(f"Failed to load SentenceTransformer model. Ensure you have an internet connection or the model is cached. Error: {e}")

        # Core intent definitions. These cover the primary actions a user can take.
        self.intents = {
            "query_data": ["show me", "what is", "get", "display", "list", "find", "tell me about"],
            "aggregate_data": ["total", "sum", "average", "count", "maximum", "minimum", "how many"],
            "trend_analysis": ["trend", "over time", "growth", "change", "timeline", "history", "by month", "by year"],
            "comparison": ["compare", "versus", "vs", "difference between"],
            "top_bottom_filter": ["top", "bottom", "best", "worst", "highest", "lowest", "most", "least"],
            "general_question": ["why", "how", "explain", "what does this mean"]
        }
        print("✓ Intent Classifier is ready (in simplified, generalist mode).")

    def classify(self, prompt: str) -> Dict:
        """
        Classifies the intent of a user's prompt using semantic similarity.

        Args:
            prompt (str): The natural language input from the user.

        Returns:
            A dictionary containing the best intent, its confidence score, and all scores.
            e.g., {"intent": "aggregate_data", "confidence": 0.85, "all_scores": {...}}
        """
        if not prompt:
            return {"intent": "unknown", "confidence": 0.0, "all_scores": {}}

        prompt_lower = prompt.lower()
        prompt_emb = self.model.encode(prompt_lower, normalize_embeddings=True)

        scores = {}
        for intent, keywords in self.intents.items():
            # Create a representative sentence for the intent
            intent_text = " ".join(keywords)
            intent_emb = self.model.encode(intent_text, normalize_embeddings=True)
            
            # Calculate cosine similarity
            similarity = np.dot(prompt_emb, intent_emb)
            scores[intent] = float(similarity)

        if not scores:
            return {"intent": "unknown", "confidence": 0.0, "all_scores": {}}

        # Find the intent with the highest score
        best_intent = max(scores, key=scores.get)
        confidence = scores[best_intent]

        return {
            "intent": best_intent,
            "confidence": confidence,
            "all_scores": scores
        }