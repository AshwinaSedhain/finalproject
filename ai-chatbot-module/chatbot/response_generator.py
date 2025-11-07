# File: ai-chatbot-module/chatbot/response_generator.py

import pandas as pd
from typing import Dict, Any
from .llm_manager import FreeLLMManager

class ResponseGenerator:
    def __init__(self):
        self.llm = FreeLLMManager()
        print("✓ Polished Response Generator is ready.")

    def generate(self, user_prompt: str, query_results: pd.DataFrame, intent_data: Dict[str, Any], mode: str = 'short') -> str:
        if query_results is None or query_results.empty:
            return self._generate_no_data_template_response(user_prompt)
        else:
            return self._generate_data_response(user_prompt, query_results, intent_data, mode)

    def _generate_no_data_template_response(self, user_prompt: str) -> str:
        print("[Response Generator] No data found. Using reliable template response.")
        response = f"I could not find any data related to your request for '{user_prompt}'. This might mean there are no records matching your criteria in the database. Please try rephrasing your question or asking about something else."
        return response

    def _generate_data_response(self, user_prompt: str, query_results: pd.DataFrame, intent_data: Dict[str, Any], mode: str) -> str:
        results_markdown = query_results.to_markdown(index=False)
        
        # Determine if this is a business analytics question
        prompt_lower = user_prompt.lower()
        is_business_query = any(keyword in prompt_lower for keyword in [
            'revenue', 'sales', 'profit', 'improve', 'improvement', 'suggestion', 
            'recommend', 'analyze', 'trend', 'insight', 'performance', 'growth'
        ])
        
        task_prompt = "Briefly summarize the key findings from the data below."
        if mode == 'detailed' or is_business_query:
            task_prompt = """Provide a comprehensive business analysis of the data. Include:
1. A clear answer to the user's question with specific numbers
2. Key trends and patterns you observe
3. Business insights and what these numbers mean
4. If appropriate, 1-2 actionable recommendations for improvement

Be specific with numbers and dates. If the user asked about improvements or recommendations, provide concrete suggestions based on the data."""
        
        system_prompt = """You are an expert business data analyst AI for InsightAI. You help companies understand their data and make data-driven decisions. 
Your responses should be:
- Professional and clear
- Data-driven with specific numbers
- Actionable with business insights
- Concise but comprehensive
- Focused on helping the business improve
- **CRITICAL: Ensure perfect spelling and grammar. Double-check all words before responding.**
- **MANDATORY: Always spell "the" correctly (not "te" or "th"). Always spell "AI" correctly (not "al" or "Al").**
- **MANDATORY: Common words like "the", "hello", "many", "AI" must be spelled correctly.**
- **MANDATORY: Before sending your response, review it and fix any spelling errors, especially "Te" -> "The" and "Al" -> "AI".**

Do NOT start with greetings. Jump straight into the analysis. Always write complete, correctly spelled sentences."""
        
        prompt = f"""
USER'S ORIGINAL QUESTION: "{user_prompt}"

DATASET (result of the SQL query):
```markdown
{results_markdown}
```

YOUR TASK: {task_prompt}

IMPORTANT:
- Start immediately with the answer (no greetings)
- Use specific numbers from the data
- If asked about "improvements" or "how can it be improved", provide concrete, actionable recommendations
- For monthly/yearly trends, explain the pattern and significance
- For comparisons, highlight the key differences
- For totals/averages, put them in business context
"""
        messages = [
            {"role": "system", "content": system_prompt}, 
            {"role": "user", "content": prompt}
        ]
        # Lower temperature for more deterministic, correctly spelled responses
        response = self.llm.generate(messages, temperature=0.2, max_tokens=1024, fix_typos=True)
        
        # Post-process to fix common LLM typos that text corrector might miss
        # Fix "Te " -> "The " (common LLM error) - COMPREHENSIVE FIXES
        response = response.replace("Te customer", "The customer")
        response = response.replace("Te AI service", "The AI service")
        response = response.replace("Te AI", "The AI")
        response = response.replace("Te ai", "The AI")
        response = response.replace("te AI", "The AI")
        # CRITICAL: Fix "Te Al" -> "The AI" (common LLM typo)
        response = response.replace("Te Al", "The AI")
        response = response.replace("Te al", "The AI")
        response = response.replace("te Al", "The AI")
        response = response.replace("Al service", "AI service")
        response = response.replace("Te Al service", "The AI service")
        # Fix "Te " at start of sentences
        import re
        response = re.sub(r'\bTe\s+([A-Z])', r'The \1', response)
        response = re.sub(r'^Te\s+', 'The ', response, flags=re.MULTILINE)
        # Fix "Al" -> "AI" when it's clearly meant to be "AI"
        response = re.sub(r'\bThe\s+Al\s+service\b', 'The AI service', response, flags=re.IGNORECASE)
        response = re.sub(r'\bThe\s+Al\b', 'The AI', response, flags=re.IGNORECASE)
        # Ultimate fix: Replace ALL instances of "Te " with "The "
        response = re.sub(r'\bTe\s+', 'The ', response)
        
        return response