"""
Multi-Model LLM Manager with Automatic Fallback
Uses multiple FREE AI models for maximum reliability
"""

import os
import time
from typing import List, Dict, Optional, Tuple
from .text_corrector import TextCorrector

# Try importing each model provider
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("[Multi-Model] Groq not available. Install with: pip install groq")

try:
    import requests
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False
    print("[Multi-Model] requests not available. Install with: pip install requests")

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("[Multi-Model] Google Gemini not available. Install with: pip install google-generativeai")


class MultiModelLLMManager:
    """
    Manages multiple FREE LLM providers with automatic fallback.
    
    Priority Order (Most Reliable First):
    1. Groq (Llama 3.3 70B) - Fastest, most reliable
    2. Hugging Face (Mistral 7B) - Very reliable, good free tier
    3. Google Gemini (Gemini Pro) - Free tier, reliable backup
    """
    
    def __init__(self):
        self.text_corrector = TextCorrector()
        self.models = []
        self.model_stats = {}  # Track success/failure rates
        
        # Initialize models in priority order
        self._initialize_models()
        
        if not self.models:
            raise ValueError(
                "\n❌ No AI models available!\n"
                "   Please configure at least one API key:\n"
                "   - GROQ_API_KEY (recommended)\n"
                "   - HUGGINGFACE_API_KEY\n"
                "   - GOOGLE_API_KEY or GEMINI_API_KEY\n"
            )
        
        print(f"✓ Multi-Model Manager initialized with {len(self.models)} model(s)")
        for i, model_info in enumerate(self.models, 1):
            print(f"   {i}. {model_info['name']} ({model_info['provider']})")
    
    def _initialize_models(self):
        """Initialize all available models in priority order."""
        
        # Model 1: Groq (Primary - Fastest and Most Reliable)
        groq_key = os.getenv("GROQ_API_KEY")
        if GROQ_AVAILABLE and groq_key:
            try:
                client = Groq(api_key=groq_key)
                self.models.append({
                    'name': 'Groq Llama 3.3 70B',
                    'provider': 'groq',
                    'client': client,
                    'model': 'llama-3.3-70b-versatile',
                    'timeout': 30,
                    'enabled': True
                })
                self.model_stats['groq'] = {'success': 0, 'failures': 0}
                print("✓ Groq model initialized (Primary)")
            except Exception as e:
                print(f"⚠ Groq initialization failed: {e}")
        else:
            print("⚠ Groq not configured (GROQ_API_KEY missing)")
        
        # Model 2: Hugging Face (Fallback 1 - Very Reliable)
        hf_key = os.getenv("HUGGINGFACE_API_KEY")
        if HF_AVAILABLE and hf_key:
            try:
                # Use a more current and stable model
                # Try multiple model options in order of preference
                hf_models = [
                    'mistralai/Mistral-7B-Instruct-v0.3',  # Updated version
                    'mistralai/Mixtral-8x7B-Instruct-v0.1',  # Alternative
                    'meta-llama/Llama-3-8b-instruct',  # Llama 3 alternative
                    'google/flan-t5-large'  # Fallback option
                ]
                
                # Use the first available model (will try others if one fails)
                self.models.append({
                    'name': 'Hugging Face Mistral 7B',
                    'provider': 'huggingface',
                    'api_key': hf_key,
                    'model': hf_models[0],  # Start with most recent
                    'fallback_models': hf_models[1:],  # Try others if first fails
                    'timeout': 45,
                    'enabled': True
                })
                self.model_stats['huggingface'] = {'success': 0, 'failures': 0}
                print("✓ Hugging Face model initialized (Fallback 1)")
            except Exception as e:
                print(f"⚠ Hugging Face initialization failed: {e}")
        else:
            print("⚠ Hugging Face not configured (HUGGINGFACE_API_KEY missing)")
        
        # Model 3: Google Gemini (Fallback 2 - Free Tier, Reliable Backup)
        gemini_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if GEMINI_AVAILABLE and gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=gemini_key)
                self.models.append({
                    'name': 'Google Gemini Pro',
                    'provider': 'gemini',
                    'api_key': gemini_key,
                    'model': 'gemini-pro',  # Free tier model
                    'timeout': 45,
                    'enabled': True
                })
                self.model_stats['gemini'] = {'success': 0, 'failures': 0}
                print("✓ Google Gemini model initialized (Fallback 2)")
            except Exception as e:
                print(f"⚠ Google Gemini initialization failed: {e}")
        else:
            print("⚠ Google Gemini not configured (GOOGLE_API_KEY or GEMINI_API_KEY missing)")
    
    def _generate_with_groq(self, model_info: Dict, messages: List[Dict], 
                            temperature: float, max_tokens: int) -> str:
        """Generate response using Groq."""
        response = model_info['client'].chat.completions.create(
            model=model_info['model'],
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=model_info['timeout']
        )
        return response.choices[0].message.content
    
    def _generate_with_huggingface(self, model_info: Dict, messages: List[Dict],
                                   temperature: float, max_tokens: int) -> str:
        """Generate response using Hugging Face Inference API with fallback models."""
        api_key = model_info['api_key']
        headers = {"Authorization": f"Bearer {api_key}"}
        
        # Convert messages to prompt format
        prompt = self._messages_to_prompt(messages)
        
        # Try primary model first, then fallback models
        models_to_try = [model_info['model']]
        if 'fallback_models' in model_info:
            models_to_try.extend(model_info['fallback_models'])
        
        last_error = None
        for model_name in models_to_try:
            try:
                api_url = f"https://api-inference.huggingface.co/models/{model_name}"
                
                payload = {
                    "inputs": prompt,
                    "parameters": {
                        "temperature": temperature,
                        "max_new_tokens": max_tokens,
                        "return_full_text": False
                    }
                }
                
                response = requests.post(api_url, headers=headers, json=payload, 
                                       timeout=model_info['timeout'])
                
                # Check for 410 Gone (model deprecated) or 404 (model not found)
                if response.status_code == 410 or response.status_code == 404:
                    print(f"[Multi-Model] Model {model_name} is deprecated (410/404), trying next model...")
                    last_error = f"Model {model_name} is no longer available (410 Gone)"
                    continue  # Try next model
                
                response.raise_for_status()
                
                result = response.json()
                
                # Handle loading state (model is starting up)
                if isinstance(result, dict) and result.get('error'):
                    error_msg = result.get('error', '')
                    if 'loading' in error_msg.lower():
                        # Wait a bit and retry
                        import time
                        time.sleep(5)
                        response = requests.post(api_url, headers=headers, json=payload, 
                                               timeout=model_info['timeout'])
                        response.raise_for_status()
                        result = response.json()
                
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get('generated_text', '')
                elif isinstance(result, dict):
                    return result.get('generated_text', '')
                else:
                    raise ValueError("Unexpected response format from Hugging Face")
                    
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 410 or e.response.status_code == 404:
                    print(f"[Multi-Model] Model {model_name} unavailable (410/404), trying next...")
                    last_error = str(e)
                    continue
                else:
                    last_error = str(e)
                    if model_name == models_to_try[-1]:  # Last model, raise error
                        raise
                    continue
            except Exception as e:
                last_error = str(e)
                if model_name == models_to_try[-1]:  # Last model, raise error
                    raise
                continue
        
        # All models failed
        raise Exception(f"All Hugging Face models failed. Last error: {last_error}")
    
    def _generate_with_gemini(self, model_info: Dict, messages: List[Dict],
                              temperature: float, max_tokens: int) -> str:
        """Generate response using Google Gemini."""
        import google.generativeai as genai
        
        # Configure with API key
        genai.configure(api_key=model_info['api_key'])
        
        # Get the model
        model = genai.GenerativeModel(model_info['model'])
        
        # Convert messages to Gemini format
        # Gemini uses a single prompt string, so we combine messages
        prompt = self._messages_to_prompt(messages)
        
        # Generate response
        response = model.generate_content(
            prompt,
            generation_config={
                'temperature': temperature,
                'max_output_tokens': max_tokens,
            }
        )
        
        return response.text
    
    def _messages_to_prompt(self, messages: List[Dict]) -> str:
        """Convert messages to a single prompt string for models that need it."""
        prompt_parts = []
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            if role == 'system':
                prompt_parts.append(f"System: {content}\n")
            elif role == 'user':
                prompt_parts.append(f"User: {content}\n")
            elif role == 'assistant':
                prompt_parts.append(f"Assistant: {content}\n")
        return "\n".join(prompt_parts)
    
    def generate(
        self,
        messages: List[Dict],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        fix_typos: bool = True
    ) -> str:
        """
        Generate response using multiple models with automatic fallback.
        
        Tries models in priority order until one succeeds.
        
        Args:
            messages: List of message dictionaries
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            fix_typos: Whether to fix common typos in the response
            
        Returns:
            Generated response string
            
        Raises:
            Exception: If all models fail
        """
        last_error = None
        attempted_models = []
        total_models = len([m for m in self.models if m.get('enabled', True)])
        
        # Try each model in priority order
        model_index = 0
        for model_info in self.models:
            if not model_info.get('enabled', True):
                print(f"[Multi-Model] Skipping {model_info['name']} (disabled)")
                continue
            
            model_index += 1
            provider = model_info['provider']
            model_name = model_info['name']
            attempted_models.append(model_name)
            
            try:
                print(f"[Multi-Model] Trying {model_name} ({model_index}/{total_models})...")
                start_time = time.time()
                
                # Generate based on provider
                if provider == 'groq':
                    raw_response = self._generate_with_groq(
                        model_info, messages, temperature, max_tokens
                    )
                elif provider == 'huggingface':
                    raw_response = self._generate_with_huggingface(
                        model_info, messages, temperature, max_tokens
                    )
                elif provider == 'gemini':
                    raw_response = self._generate_with_gemini(
                        model_info, messages, temperature, max_tokens
                    )
                else:
                    continue
                
                elapsed_time = time.time() - start_time
                
                # Track success
                self.model_stats[provider]['success'] += 1
                print(f"✓ {model_name} succeeded in {elapsed_time:.2f}s")
                
                # Fix typos if requested
                if fix_typos and raw_response:
                    corrected_response = self.text_corrector.fix_llm_response(raw_response)
                    if corrected_response != raw_response:
                        print(f"[Multi-Model] Fixed typos in response from {model_name}")
                    return corrected_response
                
                return raw_response
                
            except Exception as e:
                elapsed_time = time.time() - start_time if 'start_time' in locals() else 0
                error_str = str(e).lower()
                
                # Track failure
                self.model_stats[provider]['failures'] += 1
                
                # Check if it's a retryable error or model unavailable (410/404)
                is_retryable = any(keyword in error_str for keyword in [
                    'rate limit', '429', '503', 'timeout', 'connection', 
                    'service unavailable', 'too many requests'
                ])
                
                is_model_unavailable = '410' in error_str or 'gone' in error_str or '404' in error_str or 'all hugging face models failed' in error_str
                
                if is_model_unavailable:
                    print(f"⚠ {model_name} is unavailable (deprecated/removed): {e}")
                    # Disable this model for this session
                    model_info['enabled'] = False
                elif is_retryable:
                    print(f"⚠ {model_name} failed (retryable): {e}")
                else:
                    print(f"⚠ {model_name} failed: {e}")
                
                # Check if there are more models to try
                current_model_index = self.models.index(model_info)
                remaining_models = [m for m in self.models[current_model_index + 1:] if m.get('enabled', True)]
                if remaining_models:
                    next_model = remaining_models[0]['name']
                    print(f"   → Trying next model: {next_model}...")
                else:
                    print(f"   → No more models to try.")
                
                last_error = e
                continue
        
        # All models failed - provide detailed error message
        available_models = [m['name'] for m in self.models if m.get('enabled', True)]
        error_msg = (
            f"All AI models failed after trying {len(attempted_models)} model(s).\n"
            f"Attempted: {', '.join(attempted_models)}\n"
            f"Last error: {last_error}\n"
            f"Model statistics: {self.model_stats}"
        )
        print(f"❌ {error_msg}")
        raise Exception(error_msg)
    
    def get_model_stats(self) -> Dict:
        """Get statistics about model usage."""
        stats = {}
        for provider, counts in self.model_stats.items():
            total = counts['success'] + counts['failures']
            if total > 0:
                success_rate = (counts['success'] / total) * 100
                stats[provider] = {
                    'success': counts['success'],
                    'failures': counts['failures'],
                    'success_rate': f"{success_rate:.1f}%"
                }
            else:
                stats[provider] = {
                    'success': 0,
                    'failures': 0,
                    'success_rate': 'N/A'
                }
        return stats

