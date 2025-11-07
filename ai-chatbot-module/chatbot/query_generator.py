# chatbot/query_generator.py
from typing import Dict
from .llm_manager import FreeLLMManager

class QueryGenerator:
    def __init__(self):
        self.llm = FreeLLMManager()
        print("✓ Data-Aware Query Generator is ready.")

    def _format_knowledge_base_for_prompt(self, knowledge_base: Dict) -> str:
        # ... (This function is correct, no changes needed)
        prompt_str = "DATABASE KNOWLEDGE BASE:\n\n"
        for table_name, table_data in knowledge_base.items():
            prompt_str += f"Table: `{table_name}`\nDescription: {table_data['description']}\nColumns:\n"
            for col_name, col_data in table_data['columns'].items():
                fk_info = f" ({col_data['foreign_key']})" if col_data.get('foreign_key') else ""
                prompt_str += f"  - `{col_name}` ({col_data['type']}): {col_data['description']}{fk_info}\n"
            prompt_str += "\n"
        return prompt_str

    def _build_prompt(self, user_prompt_with_history: str, intent_data: Dict, knowledge_base: Dict) -> str:
        knowledge_base_str = self._format_knowledge_base_for_prompt(knowledge_base)
        prompt = f"""
{knowledge_base_str}
---
USER'S CONVERSATION HISTORY & LATEST REQUEST:
{user_prompt_with_history}
---
DETECTED INTENT: {intent_data.get('intent', 'unknown')}
---
TASK & INSTRUCTIONS:
You are an expert SQL query generator for business analytics. Generate a single, valid PostgreSQL query that answers the user's request.

CRITICAL RULES:
1. **Time-based queries (monthly, yearly, daily):**
   - For "monthly revenue", "sales by month", use DATE_TRUNC('month', date_column) to group by month
   - For "yearly", use DATE_TRUNC('year', date_column)
   - For "daily", use DATE_TRUNC('day', date_column)
   - Always ORDER BY the time column ASC for chronological results
   - **CRITICAL DATE FORMAT HANDLING:**
     * If date column is VARCHAR/TEXT, you MUST convert it to DATE first
     * Try these formats in order (use COALESCE or CASE to handle multiple formats):
       - If dates look like "11/8/2016" or "MM/DD/YYYY": TO_DATE(date_column, 'MM/DD/YYYY')
       - If dates look like "2016-11-08" or "YYYY-MM-DD": TO_DATE(date_column, 'YYYY-MM-DD')
       - If dates look like "08-11-2016" or "DD-MM-YYYY": TO_DATE(date_column, 'DD-MM-YYYY')
     * For DATE_TRUNC with VARCHAR dates: DATE_TRUNC('month', TO_DATE(date_column, 'MM/DD/YYYY'))
     * If unsure of format, try: CAST(date_column AS DATE) first (PostgreSQL auto-detects common formats)
     * Example for MM/DD/YYYY: SELECT DATE_TRUNC('month', TO_DATE("Order Date", 'MM/DD/YYYY')) as month, SUM("Sales") as total_sales FROM superstore GROUP BY month ORDER BY month ASC;
     * Example for auto-detect: SELECT DATE_TRUNC('month', CAST("Order Date" AS DATE)) as month, SUM("Sales") as total_sales FROM superstore GROUP BY month ORDER BY month ASC;

2. **Aggregation queries:**
   - "total sales" → SUM(amount) or SUM(total)
   - "average revenue" → AVG(amount) or AVG(revenue)
   - "count of orders" → COUNT(*)
   - "maximum profit" → MAX(profit)
   - "minimum cost" → MIN(cost)

3. **Table and column matching:**
   - Match user's words to table/column descriptions in the knowledge base
   - "transaction" might map to "sales", "orders", "payments", etc. - use the description that best fits
   - "revenue" might be "amount", "total", "price", "revenue" - check column descriptions
   - "product" maps to products table, "customer" to customers table, etc.

4. **JOINs:**
   - When user asks for "sales by product name", JOIN sales with products using foreign keys
   - When user asks for "revenue by customer", JOIN sales/orders with customers
   - Always use proper JOIN syntax (INNER JOIN, LEFT JOIN) based on the relationship

5. **Business metrics:**
   - "monthly revenue" → Group sales/transactions by month, sum amounts
   - "total sales" → Sum all sales amounts
   - "top products" → GROUP BY product, ORDER BY SUM(amount) DESC, LIMIT 10
   - "customer analysis" → Group by customer, aggregate sales/revenue

6. **Filtering:**
   - Use ILIKE for text searches (case-insensitive): WHERE name ILIKE '%search%'
   - Use proper date filters: 
     * If date column is DATE/TIMESTAMP: WHERE date_column >= '2024-01-01'
     * If date column is VARCHAR/TEXT: WHERE TO_DATE(date_column, 'MM/DD/YYYY') >= '2024-01-01' OR CAST(date_column AS DATE) >= '2024-01-01'
   - Use proper comparisons: WHERE amount > 1000

7. **Output format:**
   - Always include meaningful column aliases (AS month, AS total_revenue, AS product_name)
   - For time series, include the time column
   - For aggregations, include the metric column

8. **Error prevention:**
   - Always use table aliases when joining
   - Use proper NULL handling: COALESCE(column, 0) for numeric aggregations
   - Use DISTINCT if needed to avoid duplicates

IMPORTANT: Respond with ONLY the raw SQL query. No explanations, no markdown, no code blocks. Just the SQL.
"""
        return prompt

    def generate_sql(self, user_prompt_with_history: str, intent_data: Dict, knowledge_base: Dict) -> str:
        prompt = self._build_prompt(user_prompt_with_history, intent_data, knowledge_base)
        messages = [
            {
                "role": "system", 
                "content": "You are an expert SQL generator specializing in PostgreSQL. You generate accurate, efficient SQL queries for business analytics. Always return ONLY the SQL query, nothing else."
            }, 
            {"role": "user", "content": prompt}
        ]
        sql = self.llm.generate(messages, temperature=0.1, max_tokens=1024)
        return self._clean_sql(sql)

    def _clean_sql(self, sql: str) -> str:
        # ... (This function is correct, no changes needed)
        sql = sql.replace("```sql", "").replace("```", "")
        select_pos = sql.upper().find("SELECT")
        if select_pos > 0: sql = sql[select_pos:]
        return sql.strip().rstrip(';')