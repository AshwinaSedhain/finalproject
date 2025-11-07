# File: ai-chatbot-module/chatbot/agent.py

import json
import traceback
from typing import Dict, Any, Callable, Optional
from spellchecker import SpellChecker

from .llm_manager import FreeLLMManager
from .intent_classifier import IntentClassifier
from .query_generator import QueryGenerator
from .response_generator import ResponseGenerator
from .visualizer import AutoVisualizer
from .supabase_manager import SupabaseManager
from .cache_manager import SimpleCacheManager
from .activity_logger import ActivityLogger

class ChatbotAgent:
    def __init__(self):
        print("\n" + "="*70); print("Initializing AI Chatbot Agent..."); print("="*70)
        self.llm_manager = FreeLLMManager()
        self.intent_classifier = IntentClassifier()
        self.query_generator = QueryGenerator()
        self.response_generator = ResponseGenerator()
        self.visualizer = AutoVisualizer()
        self.supabase_manager = SupabaseManager()
        self.cache_manager = SimpleCacheManager()
        self.activity_logger = ActivityLogger()
        self.last_interaction_by_user: Dict[str, Dict[str, Any]] = {}
        try:
            with open("knowledge_base.json", 'r') as f:
                self.knowledge_base = json.load(f)
            print("✓ Knowledge Base ('knowledge_base.json') loaded successfully.")
        except Exception as e:
            print(f"🔥 CRITICAL ERROR loading knowledge_base.json: {e}")
            self.knowledge_base = None
        print("="*70); print("✅ Agent initialized!"); print("="*70 + "\n")

    def _get_corrected_prompt(self, prompt: str, prompt_type: str = None) -> str:
        """
        Only apply spell checking to data queries, not general conversation.
        This prevents incorrect corrections in jokes and casual conversation.
        """
        # Skip spell checking for general conversation to avoid incorrect corrections
        if prompt_type == "general_conversation":
            return prompt
        
        # Only apply spell checking to data queries where accuracy matters
        try:
            spell = SpellChecker()
            words = prompt.split()
            # Filter out punctuation and numbers
            words_to_check = [w.lower().strip('.,!?;:()[]{}"\'') for w in words if w.isalpha()]
            misspelled = spell.unknown(words_to_check)
            
            if not misspelled:
                return prompt
            
            # Only correct if confidence is high (word is clearly misspelled)
            corrected_words = []
            for word in words:
                cleaned_word = word.lower().strip('.,!?;:()[]{}"\'')
                if cleaned_word in misspelled and word.isalpha():
                    correction = spell.correction(cleaned_word)
                    # Only apply correction if it's significantly different and likely correct
                    if correction and correction != cleaned_word and len(correction) >= len(cleaned_word) * 0.8:
                        # Preserve original casing
                        if word[0].isupper():
                            corrected_words.append(correction.capitalize())
                        else:
                            corrected_words.append(correction)
                    else:
                        corrected_words.append(word)
                else:
                    corrected_words.append(word)
            
            corrected_prompt = " ".join(corrected_words)
            if corrected_prompt.lower() != prompt.lower():
                print(f"[Agent Auto-Correct] Original: '{prompt}' -> Corrected: '{corrected_prompt}'")
                return corrected_prompt
        except Exception as e:
            print(f"[Warning] Spell check failed: {e}. Using original prompt.")
        
        return prompt

    def _classify_prompt_type(self, prompt: str) -> str:
        """
        Classify prompt type. Use simple keyword matching for speed, fallback to LLM if uncertain.
        """
        prompt_lower = prompt.lower()
        
        # Quick checks for general conversation (jokes, greetings, casual chat)
        general_keywords = [
            'joke', 'hello', 'hi', 'hey', 'thanks', 'thank you', 'bye', 'goodbye',
            'who are you', 'what are you', 'what is your name', 'how do you work',
            'tell me about yourself', 'what can you do'
        ]
        if any(keyword in prompt_lower for keyword in general_keywords):
            return "general_conversation"
        
        # Quick checks for data queries (numbers, metrics, business questions)
        data_keywords = [
            'show me', 'what is', 'how much', 'how many', 'total', 'sum', 'average',
            'revenue', 'sales', 'profit', 'transaction', 'monthly', 'yearly', 'daily',
            'list', 'find', 'get', 'display', 'tell me about', 'analyze', 'compare',
            'top', 'bottom', 'best', 'worst', 'improve', 'improvement', 'suggestion',
            'recommend', 'trend', 'growth', 'performance', 'insight'
        ]
        if any(keyword in prompt_lower for keyword in data_keywords):
            return "data_query"
        
        # Meta queries (about the database or system)
        meta_keywords = [
            'what tables', 'what columns', 'what schema', 'database structure',
            'can you', 'what can', 'how can', 'show database', 'show schema'
        ]
        if any(keyword in prompt_lower for keyword in meta_keywords):
            return "meta_query"
        
        # Fallback to LLM for uncertain cases
        system_prompt = """
        You are a highly accurate request classifier. Classify the user's prompt into one of three categories:

        1. 'data_query': Asking for specific information, numbers, lists, calculations, or business analysis from a database.
        2. 'meta_query': Asking ABOUT the database structure, tables, or AI capabilities.
        3. 'general_conversation': Greetings, jokes, casual conversation, or questions about the AI itself.

        Respond with ONLY the category name in lowercase.
        """
        try:
            response = self.llm_manager.generate(
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": f"Classify: '{prompt}'"}],
                temperature=0.0, max_tokens=20
            )
            cleaned_response = response.lower().strip().replace("'", "").replace('"', '')
            if "data_query" in cleaned_response: return "data_query"
            if "meta_query" in cleaned_response: return "meta_query"
            return "general_conversation"
        except Exception:
            # Default to data_query if LLM fails (safer default)
            return "data_query"

    def _handle_error(self, user_id: str, prompt: str, e: Exception) -> Dict[str, Any]:
        error_str = str(e).lower()
        error_type = type(e).__name__
        print(f"🔥 An error occurred: {error_type}: {e}")
        traceback.print_exc()
        
        # Provide more helpful error messages based on error type
        if "connection" in error_str or "database" in error_str or "connectionpool" in error_str:
            error_response = "I'm having trouble connecting to the database. Please check your database connection settings or contact support."
        elif "sql" in error_str or "query" in error_str or "syntax" in error_str:
            error_response = "I had difficulty generating a valid query for your request. Could you try rephrasing your question or being more specific about what data you'd like to see?"
        elif "llm" in error_str or "api" in error_str or "groq" in error_str or "rate limit" in error_str or "429" in error_str or "all ai models failed" in error_str or "410" in error_str or "all hugging face models failed" in error_str:
            if "rate limit" in error_str or "429" in error_str:
                # HARDCODED: Use exact string to avoid any typos
                # Use a constant to ensure it never gets modified
                ERROR_MSG_RATE_LIMIT = "The AI service is currently experiencing high demand. Please wait a moment and try again."
                error_response = ERROR_MSG_RATE_LIMIT
                # CRITICAL: Ensure it stays as "The AI" - fix any typos that might have been introduced
                # Fix "Th " -> "The " (common LLM typo)
                error_response = error_response.replace("Th AI", "The AI").replace("Th ai", "The AI")
                error_response = error_response.replace("Th ", "The ")
                # Fix "Te " -> "The " (another common typo)
                error_response = error_response.replace("Te AI", "The AI").replace("Te ai", "The AI")
                error_response = error_response.replace("Te ", "The ")
                # Final verification - ensure it starts with "The "
                if error_response.startswith("Th "):
                    error_response = "The " + error_response[3:]
                if error_response.startswith("Te "):
                    error_response = "The " + error_response[3:]
                result = {"success": False, "response": error_response, "error": str(e), "error_type": error_type}
                self.activity_logger.log(user_id, prompt, result)
                return result
            elif "410" in error_str or "gone" in error_str:
                # Model deprecated - but system should try others
                error_response = "One AI model is temporarily unavailable. The system is automatically trying alternative models. Please wait a moment..."
            elif "all ai models failed" in error_str or "all hugging face models failed" in error_str or "all models failed" in error_str:
                # All models failed - provide helpful message with guidance
                error_response = (
                    "I'm unable to connect to any AI service at the moment. "
                    "This could be due to:\n"
                    "- Network connectivity issues\n"
                    "- API key configuration problems\n"
                    "- All AI services being temporarily unavailable\n\n"
                    "Please check your API keys in the .env file and try again in a few moments. "
                    "The system will automatically retry with different models."
                )
            elif "authentication" in error_str or "401" in error_str or "403" in error_str:
                error_response = "AI service authentication failed. Please contact support."
            elif "timeout" in error_str:
                error_response = "The AI service request timed out. Please try again."
            else:
                # Fix any typos in the exception message first
                error_msg = str(e)[:150].replace("Th AI", "The AI").replace("Th ai", "The AI").replace("Th ", "The ")
                error_response = f"I'm experiencing issues with the AI service: {error_msg}. Please try again in a moment. If the problem persists, contact support."
                # Ensure the error response itself doesn't have typos
                error_response = error_response.replace("Th AI", "The AI").replace("Th ai", "The AI").replace("Th ", "The ")
        elif "knowledge" in error_str or "schema" in error_str:
            error_response = "The database schema information is not available. Please contact an administrator to set up the knowledge base."
        else:
            error_response = f"I encountered an unexpected error: {str(e)[:150]}. Please try rephrasing your question or contact support if the issue persists."
        
        # Fix typos in error response (e.g., "Th AI" -> "The AI", "Te AI" -> "The AI")
        # CRITICAL: Fix "Th " -> "The " directly first (before text corrector)
        if "Th AI" in error_response or "Th ai" in error_response:
            error_response = error_response.replace("Th AI", "The AI").replace("Th ai", "The AI")
        if error_response.startswith("Th "):
            error_response = "The " + error_response[3:]
        
        # Fix "Te AI" -> "The AI" before text corrector
        error_response = error_response.replace("Te AI", "The AI").replace("Te ai", "The AI").replace("te AI", "The AI")
        
        # Then apply full text corrector
        try:
            error_response = self.llm_manager.text_corrector.fix_llm_response(error_response)
        except Exception as e:
            print(f"[Agent] Text corrector failed: {e}, using direct fix result")
            # If text corrector fails, ensure we still have the direct fix
            if "Th AI" in error_response or "Th ai" in error_response:
                error_response = error_response.replace("Th AI", "The AI").replace("Th ai", "The AI")
            if "Te AI" in error_response or "Te ai" in error_response:
                error_response = error_response.replace("Te AI", "The AI").replace("Te ai", "The AI")
        
        # Final safeguard: Ensure "The AI" is correct
        error_response = error_response.replace("Te AI", "The AI").replace("Te ai", "The AI").replace("te AI", "The AI")
        
        result = {"success": False, "response": error_response, "error": str(e), "error_type": error_type}
        self.activity_logger.log(user_id, prompt, result)
        return result
    
    def _fix_date_format_in_sql(self, sql: str) -> str:
        """
        Attempts to fix common date format issues in SQL queries.
        Replaces 'yyyy-mm-dd' with 'MM/DD/YYYY' and other common fixes.
        """
        import re
        fixed_sql = sql
        
        # Fix TO_DATE with 'yyyy-mm-dd' -> 'MM/DD/YYYY' (most common issue)
        fixed_sql = re.sub(
            r"TO_DATE\(([^,]+),\s*['\"]yyyy-mm-dd['\"]\)",
            r"TO_DATE(\1, 'MM/DD/YYYY')",
            fixed_sql,
            flags=re.IGNORECASE
        )
        
        # Also try CAST as DATE (more forgiving)
        # If TO_DATE still fails, replace with CAST
        if "TO_DATE" in fixed_sql and "MM/DD/YYYY" in fixed_sql:
            # Try CAST as a fallback
            fixed_sql = re.sub(
                r"TO_DATE\(([^,]+),\s*['\"]MM/DD/YYYY['\"]\)",
                r"CAST(\1 AS DATE)",
                fixed_sql,
                flags=re.IGNORECASE
            )
        
        # Fix DATE_TRUNC with TO_DATE('yyyy-mm-dd') -> TO_DATE('MM/DD/YYYY')
        def fix_date_trunc(match):
            trunc_unit = match.group(1)  # 'month', 'year', 'day', etc.
            date_col = match.group(2)
            return f"DATE_TRUNC('{trunc_unit}', TO_DATE({date_col}, 'MM/DD/YYYY'))"
        
        fixed_sql = re.sub(
            r"DATE_TRUNC\((['\"]\w+['\"]),\s*TO_DATE\(([^,]+),\s*['\"]yyyy-mm-dd['\"]\)\)",
            fix_date_trunc,
            fixed_sql,
            flags=re.IGNORECASE
        )
        
        return fixed_sql

    def process(self, user_prompt: str, user_id: str, execute_query: Optional[Callable] = None) -> Dict[str, Any]:
        if not self.knowledge_base or len(self.knowledge_base) == 0:
            return {"success": False, "response": "Knowledge base not configured. Please contact an administrator."}
        try:
            print(f"[Agent] Starting to process query: '{user_prompt[:50]}...'")
            # First classify the prompt type BEFORE spell checking
            prompt_type = self._classify_prompt_type(user_prompt)
            print(f"[Agent Triage] Classified prompt as: '{prompt_type}'")
            
            # Only apply spell checking to data queries
            corrected_prompt = self._get_corrected_prompt(user_prompt, prompt_type)

            if prompt_type == "general_conversation":
                ai_response = self.llm_manager.generate(messages=[
                    {"role": "system", "content": "You are a helpful AI assistant for InsightAI, a data analytics platform. Answer the user's general question concisely and professionally. If they ask for jokes, tell jokes naturally without correcting spelling unless it's clearly wrong. Keep responses friendly and conversational. **IMPORTANT: Ensure perfect spelling and grammar in all responses. Common words like 'the', 'hello', 'many' must be spelled correctly.**"},
                    {"role": "user", "content": user_prompt}  # Use original prompt for general conversation
                ], temperature=0.3, max_tokens=512, fix_typos=True)
                result = {"success": True, "response": ai_response}
                self.supabase_manager.add_to_history(user_id, user_prompt, ai_response)
                self.activity_logger.log(user_id, user_prompt, result)
                return result

            # The rest of the logic for data and meta queries
            cached_result = self.cache_manager.get(corrected_prompt, user_id)
            if cached_result:
                cached_result["from_cache"] = True
                return cached_result
            
            print(f"[Agent] Getting conversation history...")
            conversation_history = self.supabase_manager.get_history(user_id)
            print(f"[Agent] Classifying intent...")
            intent_data = self.intent_classifier.classify(corrected_prompt)
            print(f"[Agent] Intent: {intent_data.get('intent', 'unknown')}")
            full_prompt_for_sql = f"History:\n{conversation_history}\n\nLatest Request: {corrected_prompt}"
            print(f"[Agent] Generating SQL query...")
            generated_query = self.query_generator.generate_sql(full_prompt_for_sql, intent_data, self.knowledge_base)
            print(f"[Agent] SQL generated: {generated_query[:100] if generated_query else 'None'}...")

            if not generated_query or not generated_query.strip().upper().startswith("SELECT"):
                error_msg = f"I had trouble generating a SQL query for your request. The generated query was invalid: '{generated_query[:100]}...'. Please try rephrasing your question or being more specific about what data you'd like to see."
                return {"success": False, "response": error_msg, "error": "Invalid SQL generated"}

            query_results = None
            if execute_query:
                try:
                    print(f"[Agent] Executing SQL query...")
                    query_results = execute_query(generated_query)
                    print(f"[Agent] Query executed, got {len(query_results) if hasattr(query_results, '__len__') else 'unknown'} rows")
                except Exception as db_error:
                    error_str = str(db_error).lower()
                    print(f"[Agent] Database error: {db_error}")
                    
                    # Check if it's a date format error
                    if "datetimefieldeverflow" in error_str or "date/time field value out of range" in error_str:
                        print(f"[Agent] Detected date format error. Attempting to fix SQL...")
                        # Try to fix the date format in the SQL
                        fixed_query = self._fix_date_format_in_sql(generated_query)
                        if fixed_query != generated_query:
                            try:
                                print(f"[Agent] Retrying with fixed date format...")
                                query_results = execute_query(fixed_query)
                                print(f"[Agent] Query executed successfully after date format fix!")
                                generated_query = fixed_query  # Update to use the fixed query
                            except Exception as retry_error:
                                print(f"[Agent] Retry with fixed date format also failed: {retry_error}")
                                error_msg = f"I encountered a date format error. The dates in your database might be in a different format (like MM/DD/YYYY instead of YYYY-MM-DD). Could you try rephrasing your question or specify the date format?"
                                return {"success": False, "response": error_msg, "error": str(db_error), "generated_query": generated_query}
                        else:
                            error_msg = f"I encountered a date format error. The dates in your database might be in a different format. Could you try rephrasing your question?"
                            return {"success": False, "response": error_msg, "error": str(db_error), "generated_query": generated_query}
                    else:
                        error_msg = f"I encountered an error while querying the database: {str(db_error)}. The query I generated might not match your database schema. Could you try rephrasing your question or being more specific about what data you'd like to see?"
                        return {"success": False, "response": error_msg, "error": str(db_error), "generated_query": generated_query}
            
            print(f"[Agent] Generating response text...")
            response_text = self.response_generator.generate(corrected_prompt, query_results, intent_data)
            
            # FINAL SAFEGUARD: Use text corrector to fix ALL typos comprehensively
            # This ensures "Te" -> "The" and "Al" -> "AI" are fixed everywhere
            if response_text:
                # Use the text corrector for comprehensive fixes
                response_text = self.llm_manager.text_corrector.fix_llm_response(response_text)
                # Additional aggressive fixes as final pass
                import re
                # Fix "Te " -> "The " (all instances)
                response_text = re.sub(r'\bTe\s+', 'The ', response_text)
                response_text = re.sub(r'^Te\s+', 'The ', response_text, flags=re.MULTILINE)
                # Fix "Al" -> "AI" when it's clearly meant to be "AI"
                response_text = re.sub(r'\bThe\s+Al\b', 'The AI', response_text, flags=re.IGNORECASE)
                response_text = re.sub(r'\bAl\s+service\b', 'AI service', response_text, flags=re.IGNORECASE)
                # Final string replacements for common patterns
                response_text = response_text.replace('Te Al', 'The AI')
                response_text = response_text.replace('Te Al service', 'The AI service')
                response_text = response_text.replace('Al service', 'AI service')
                print(f"[Agent] Applied final typo correction pass")
            
            print(f"[Agent] Creating visualization...")
            visualization, chart_type = self.visualizer.create_chart(query_results, corrected_prompt, intent_data['intent'])
            print(f"[Agent] Processing complete!")
            
            result = {"success": True, "response": response_text, "intent": intent_data, "generated_query": generated_query, "visualization": visualization, "chart_type": chart_type}
            
            self.supabase_manager.add_to_history(user_id, user_prompt, result['response'])
            self.cache_manager.set(corrected_prompt, user_id, result)
            self.activity_logger.log(user_id, user_prompt, result)
            
            return result
        except Exception as e:
            return self._handle_error(user_id, user_prompt, e)