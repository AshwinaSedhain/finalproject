"""
AI Chatbot Module
Natural Language to SQL Conversion with Auto-Visualization
"""

from .agent import ChatbotAgent
from .visualizer import AutoVisualizer

__version__ = "2.0.0"
__all__ = ["ChatbotAgent", "AutoVisualizer"]

print("Chatbot module loaded (with visualization support)")