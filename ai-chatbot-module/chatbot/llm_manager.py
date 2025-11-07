"""
FREE LLM Manager - Multi-Model with Automatic Fallback
Uses multiple FREE AI models for maximum reliability
"""

import os
from typing import List, Dict

# Try to use Multi-Model Manager, fallback to single Groq if not available
try:
    from .multi_model_manager import MultiModelLLMManager
    MULTI_MODEL_AVAILABLE = True
except ImportError:
    MULTI_MODEL_AVAILABLE = False
    print("[LLM Manager] Multi-model manager not available, using single Groq model")

# Fallback to single Groq model
if not MULTI_MODEL_AVAILABLE:
    from groq import Groq
    from .text_corrector import TextCorrector


class FreeLLMManager:
    """
    Manages FREE LLM with automatic fallback to multiple models.
    
    Uses Multi-Model Manager if available (Groq + Hugging Face + Google Gemini),
    otherwise falls back to single Groq model.
    """
    
    def __init__(self):
        if MULTI_MODEL_AVAILABLE:
            # Use multi-model manager with automatic fallback
            try:
                self.llm_backend = MultiModelLLMManager()
                self.text_corrector = self.llm_backend.text_corrector
                self.is_multi_model = True
                print("✓ Using Multi-Model Manager (with automatic fallback)")
            except Exception as e:
                print(f"⚠ Multi-Model Manager failed: {e}, falling back to single Groq")
                self._init_single_groq()
        else:
            # Fallback to single Groq model
            self._init_single_groq()
    
    def _init_single_groq(self):
        """Initialize single Groq model (fallback)."""
        groq_key = os.getenv("GROQ_API_KEY")
        
        if not groq_key:
            raise ValueError(
                "\n GROQ_API_KEY not found in environment variables!\n"
                "   Get FREE key from: https://console.groq.com\n"
                "   Then create .env file with: GROQ_API_KEY=your_key_here\n"
            )
        
        try:
            self.client = Groq(api_key=groq_key)
            self.text_corrector = TextCorrector()
            self.is_multi_model = False
            print("✓ Using single Groq model (fallback mode)")
        except Exception as e:
            raise Exception(f"Failed to initialize Groq: {e}")
    
    def generate(
        self,
        messages: List[Dict],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        fix_typos: bool = True
    ) -> str:
        """
        Generate response using multi-model system with automatic fallback.
        
        Args:
            messages: List of message dictionaries
            temperature: Sampling temperature (lower = more deterministic)
            max_tokens: Maximum tokens to generate
            fix_typos: Whether to fix common typos in the response
            
        Returns:
            Generated response string
        """
        
        if self.is_multi_model:
            # Use multi-model manager (automatic fallback)
            return self.llm_backend.generate(messages, temperature, max_tokens, fix_typos)
        else:
            # Fallback to single Groq model
            try:
                response = self.client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                raw_response = response.choices[0].message.content
                
                # Fix common typos in LLM responses
                if fix_typos and raw_response:
                    corrected_response = self.text_corrector.fix_llm_response(raw_response)
                    # Log if there was a change (for debugging)
                    if corrected_response != raw_response:
                        # Check specifically for "hllo" fix
                        if 'hllo' in raw_response.lower():
                            print(f"[LLM Manager] Fixed 'hllo' typo in response")
                        else:
                            print(f"[LLM Manager] Fixed typos in response")
                    return corrected_response
                
                return raw_response
            
            except Exception as e:
                raise Exception(f"LLM generation failed: {e}")
