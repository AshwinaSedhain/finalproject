# schema_introspector.py
"""
A utility script to introspect a database and create an enriched,
LLM-friendly schema description (a "knowledge base").
"""
import json
import os
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv

# Import the LLM manager from your chatbot module
from chatbot.llm_manager import FreeLLMManager

def generate_description(llm, item_type: str, item_name: str, parent_name: str = None) -> str:
    """Uses an LLM to generate a plain-English description for a DB object."""
    if parent_name:
        prompt = f"The database table is named '{parent_name}'. Generate a very concise, one-sentence, business-focused description for the column named '{item_name}'."
    else:
        prompt = f"Generate a very concise, one-sentence, business-focused description for a database table named '{item_name}'."
    
    description = llm.generate(
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=60
    )
    # Clean up the response
    return description.strip().replace('"', '')

def introspect_and_enrich_schema():
    """
    Connects to the database, introspects its schema, enriches it with
    LLM-generated descriptions, and saves it to a JSON file.
    """
    print("🚀 Starting Database Schema Introspection and Enrichment...")
    
    load_dotenv()
    llm = FreeLLMManager()
    
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL not found in .env file. Please add it.")
        return
        
    try:
        engine = create_engine(db_url)
        inspector = inspect(engine)
    except Exception as e:
        print(f"❌ Failed to connect to the database: {e}"); return

    enriched_schema = {}
    table_names = inspector.get_table_names()
    print(f"Found {len(table_names)} tables: {', '.join(table_names)}")

    for table_name in table_names:
        print(f"\nProcessing table: '{table_name}'...")
        
        table_desc = generate_description(llm, "table", table_name)
        print(f"  -> Generated Description: {table_desc}")
        
        enriched_schema[table_name] = {
            "description": table_desc,
            "columns": {}
        }
        
        columns = inspector.get_columns(table_name)
        foreign_keys = {fk['constrained_columns'][0]: fk for fk in inspector.get_foreign_keys(table_name)}

        for column in columns:
            col_name = column['name']
            col_type = str(column['type'])
            col_desc = generate_description(llm, "column", col_name, parent_name=table_name)
            
            column_info = {
                "type": col_type,
                "description": col_desc,
                "is_primary_key": column.get('primary_key', False),
                "foreign_key": None
            }
            
            if col_name in foreign_keys:
                fk_info = foreign_keys[col_name]
                ref_table = fk_info['referred_table']
                ref_column = fk_info['referred_columns'][0]
                column_info["foreign_key"] = f"references {ref_table}({ref_column})"
                print(f"    - Column '{col_name}' ({col_type}): {col_desc} [FK to {ref_table}]")
            else:
                print(f"    - Column '{col_name}' ({col_type}): {col_desc}")

            enriched_schema[table_name]["columns"][col_name] = column_info
    
    output_filename = "knowledge_base.json"
    with open(output_filename, 'w') as f:
        json.dump(enriched_schema, f, indent=2)
        
    print(f"\n✅ Success! Enriched schema saved to '{output_filename}'")

if __name__ == "__main__":
    introspect_and_enrich_schema()