# ai-chatbot-module/main.py
import os
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv
import json
from typing import Optional, Dict

# Load environment variables
load_dotenv()

# Import your powerful agent
from chatbot.agent import ChatbotAgent
from chatbot.llm_manager import FreeLLMManager

# --- FastAPI App Initialization ---
app = FastAPI(
    title="AI Report & Insights API",
    description="An API service for the data-aware AI chatbot.",
    version="1.0.0"
)

# --- Global variables (loaded once at startup) ---
chatbot_agent: ChatbotAgent = None
db_engine = None
# Cache for dynamic database engines (keyed by connection string)
db_engine_cache = {}
# Cache for knowledge bases per connection string
knowledge_base_cache = {}

# --- Startup Event Handler ---
@app.on_event("startup")
def startup_event():
    global chatbot_agent, db_engine
    print("--- AI Service is starting up... ---")
    try:
        chatbot_agent = ChatbotAgent()
        if not chatbot_agent.knowledge_base:
            raise RuntimeError("Knowledge Base not loaded. Run schema_introspector.py first.")
            
        db_url = os.environ.get("DATABASE_URL")
        if not db_url:
            raise ValueError("DATABASE_URL not found in .env file.")
        db_engine = create_engine(db_url)
        
        with db_engine.connect() as connection:
            print("✓ Database connection for query execution is successful.")
            
    except Exception as e:
        print(f"🔥 CRITICAL STARTUP ERROR: {e}")
        chatbot_agent = None 
        db_engine = None

# --- Pydantic Model for Request Body ---
class ChatRequest(BaseModel):
    user_prompt: str
    user_id: str
    connection_string: Optional[str] = None  # Optional: if provided, use this instead of default

class RegenerateKnowledgeBaseRequest(BaseModel):
    connection_string: str

class ClearOldConnectionsRequest(BaseModel):
    old_connection_string: Optional[str] = None

# --- API Endpoints ---
@app.get("/", tags=["Health Check"])
def read_root():
    return {"status": "AI Chatbot Service is online"}

@app.post("/process-query", tags=["Chatbot"])
async def process_query(chat_request: ChatRequest):
    if not chatbot_agent:
        raise HTTPException(status_code=503, detail="Service is not ready due to a startup error.")

    # Determine which database engine to use
    target_db_url = chat_request.connection_string if chat_request.connection_string else os.environ.get("DATABASE_URL")
    
    if not target_db_url:
        raise HTTPException(status_code=400, detail="No database connection string provided. Please configure database connection.")
    
    # Get or create engine for this connection string
    if target_db_url not in db_engine_cache:
        try:
            db_engine_cache[target_db_url] = create_engine(target_db_url)
            # Test connection
            with db_engine_cache[target_db_url].connect() as connection:
                print(f"✓ Created new database connection for: {target_db_url[:50]}...")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to connect to database: {str(e)}")
    
    current_db_engine = db_engine_cache[target_db_url]
    
    # Get or generate knowledge base for this connection string
    if target_db_url not in knowledge_base_cache:
        # Generate knowledge base for this database (optimized for speed - no LLM calls)
        try:
            print(f"[Chat] Generating knowledge base for new database connection (fast mode)...")
            inspector = inspect(current_db_engine)
            enriched_schema = {}
            table_names = inspector.get_table_names()
            
            # Limit to first 20 tables for speed (can be increased if needed)
            for table_name in table_names[:20]:
                # Simple description based on table name (no LLM call for speed)
                table_desc = table_name.replace('_', ' ').title() + " table"
                enriched_schema[table_name] = {
                    "description": table_desc,
                    "columns": {}
                }
                
                columns = inspector.get_columns(table_name)
                foreign_keys = {fk['constrained_columns'][0]: fk for fk in inspector.get_foreign_keys(table_name)}
                
                for column in columns:
                    col_name = column['name']
                    col_type = str(column['type'])
                    # Simple description based on column name (no LLM call for speed)
                    col_desc = col_name.replace('_', ' ').title()
                    
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
                    
                    enriched_schema[table_name]["columns"][col_name] = column_info
            
            knowledge_base_cache[target_db_url] = enriched_schema
            print(f"✓ Generated knowledge base for {len(enriched_schema)} tables (fast mode)")
        except Exception as e:
            print(f"Warning: Failed to generate knowledge base, using default: {e}")
            import traceback
            traceback.print_exc()
            # Fall back to default knowledge base
            knowledge_base_cache[target_db_url] = chatbot_agent.knowledge_base if chatbot_agent.knowledge_base else {}
    
    # Temporarily set the agent's knowledge base to the one for this connection
    original_kb = chatbot_agent.knowledge_base
    kb_to_use = knowledge_base_cache.get(target_db_url, {})
    
    # Ensure we have a valid knowledge base
    if not kb_to_use:
        print(f"[Chat] Warning: No knowledge base for connection, using default")
        kb_to_use = chatbot_agent.knowledge_base if chatbot_agent.knowledge_base else {}
    
    chatbot_agent.knowledge_base = kb_to_use

    def execute_query_sync(sql: str) -> pd.DataFrame:
        try:
            return pd.read_sql(sql, current_db_engine)
        except Exception as e:
            raise Exception(f"Database execution error: {e}")

    try:
        print(f"[Chat] Processing query: '{chat_request.user_prompt[:50]}...'")
        result = chatbot_agent.process(
            user_prompt=chat_request.user_prompt,
            user_id=chat_request.user_id,
            execute_query=execute_query_sync
        )
        print(f"[Chat] Query processed successfully")
        
        # Handle visualization - convert Plotly figure to JSON if it's a figure object
        if result.get('visualization') is not None:
            viz = result['visualization']
            # Check if it's a Plotly figure object (has to_json method)
            if hasattr(viz, 'to_json'):
                try:
                    result['visualization'] = viz.to_json()
                except Exception as viz_error:
                    print(f"Warning: Failed to convert visualization to JSON: {viz_error}")
                    result['visualization'] = None
            # If it's already a string, keep it as is
            elif isinstance(viz, str):
                result['visualization'] = viz
            # Otherwise, set to None
            else:
                result['visualization'] = None
        if result.get('query_results') is not None:
            del result['query_results']

        return result
    except Exception as e:
        print(f"Error processing request: {e}")
        import traceback
        traceback.print_exc()
        # Provide a user-friendly error message
        error_detail = str(e)
        if "'str' object has no attribute 'to_json'" in error_detail:
            error_detail = "Visualization processing error. Please try again."
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {error_detail}")
    finally:
        # Always restore original knowledge base
        chatbot_agent.knowledge_base = original_kb

@app.get("/dashboard/analytics", tags=["Dashboard"])
def get_dashboard_analytics(connection_string: Optional[str] = None):
    """
    Returns dynamic dashboard analytics data based on the connected database.
    """
    if not chatbot_agent:
        raise HTTPException(status_code=503, detail="Service is not ready.")
    
    # Determine which database to use
    target_db_url = connection_string if connection_string else os.environ.get("DATABASE_URL")
    
    if not target_db_url:
        raise HTTPException(status_code=400, detail="No database connection string provided. Please configure database connection.")
    
    # Get or create engine for this connection string
    if target_db_url not in db_engine_cache:
        try:
            db_engine_cache[target_db_url] = create_engine(target_db_url)
            with db_engine_cache[target_db_url].connect() as connection:
                print(f"✓ Created new database connection for dashboard: {target_db_url[:50]}...")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to connect to database: {str(e)}")
    
    # Get or generate knowledge base for this connection string
    if target_db_url not in knowledge_base_cache:
        # Generate knowledge base for this database (simplified for speed)
        try:
            print(f"Generating knowledge base for dashboard database connection...")
            current_engine = db_engine_cache[target_db_url]
            inspector = inspect(current_engine)
            enriched_schema = {}
            table_names = inspector.get_table_names()
            
            # For dashboard, use simpler schema without LLM descriptions for speed
            # We can infer descriptions from column names
            for table_name in table_names[:10]:  # Limit to first 10 tables for speed
                enriched_schema[table_name] = {
                    "description": f"Table containing {table_name} data",
                    "columns": {}
                }
                
                columns = inspector.get_columns(table_name)
                foreign_keys = {fk['constrained_columns'][0]: fk for fk in inspector.get_foreign_keys(table_name)}
                
                for column in columns:
                    col_name = column['name']
                    col_type = str(column['type'])
                    # Simple description based on column name (no LLM call for speed)
                    col_desc = col_name.replace('_', ' ').title()
                    
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
                    
                    enriched_schema[table_name]["columns"][col_name] = column_info
            
            knowledge_base_cache[target_db_url] = enriched_schema
            print(f"✓ Generated knowledge base for dashboard: {len(enriched_schema)} tables")
        except Exception as e:
            print(f"Warning: Failed to generate knowledge base for dashboard, using default: {e}")
            import traceback
            traceback.print_exc()
            # Fall back to default knowledge base or empty
            knowledge_base_cache[target_db_url] = chatbot_agent.knowledge_base if chatbot_agent.knowledge_base else {}
    
    # Use the knowledge base for this connection
    kb_to_use = knowledge_base_cache[target_db_url]
    
    try:
        from dashboard_generator import DashboardGenerator
        print(f"[Dashboard] Generating dashboard data for connection: {target_db_url[:50]}...")
        # Use the cached engine instead of creating a new one
        current_engine = db_engine_cache[target_db_url]
        generator = DashboardGenerator(target_db_url, kb_to_use)
        # Override the engine with the cached one to avoid duplicate connections
        generator.engine = current_engine
        dashboard_data = generator.generate_dashboard_data()
        print(f"[Dashboard] Dashboard data generated successfully")
        print(f"[Dashboard] Metrics count: {len(dashboard_data.get('metrics', []))}")
        print(f"[Dashboard] Has pie chart: {bool(dashboard_data.get('pieChart'))}")
        print(f"[Dashboard] Has top selling chart: {bool(dashboard_data.get('topSellingChart'))}")
        return dashboard_data
    except Exception as e:
        print(f"[Dashboard] Error generating dashboard: {e}")
        import traceback
        traceback.print_exc()
        # Return default dashboard instead of raising error
        try:
            from dashboard_generator import DashboardGenerator
            generator = DashboardGenerator(target_db_url, {})
            default_data = generator._get_default_dashboard()
            print(f"[Dashboard] Returning default dashboard due to error")
            return default_data
        except Exception as fallback_error:
            print(f"[Dashboard] Even default dashboard failed: {fallback_error}")
            raise HTTPException(status_code=500, detail=f"Failed to generate dashboard data: {str(e)}")

# 👇 --- NEW ENDPOINT ADDED HERE --- 👇
@app.get("/database-summary", tags=["Database"])
def get_database_summary():
    """
    Returns a summary of the introspected database from the knowledge_base.json file.
    """
    if not chatbot_agent or not chatbot_agent.knowledge_base:
        raise HTTPException(status_code=503, detail="Knowledge base is not loaded.")

    try:
        kb = chatbot_agent.knowledge_base
        num_tables = len(kb.keys())
        num_columns = sum(len(table_data['columns']) for table_data in kb.values())

        summary = {
            "stats": {
                "total_tables": num_tables,
                "total_rows": "N/A", # Live counting is a more advanced feature
                "total_columns": num_columns,
                "database_size": "N/A"
            },
            "insights": [
                f"Successfully analyzed the database structure.",
                f"Found {num_tables} tables, including '{next(iter(kb.keys()))}' and others.",
                "The AI is ready to answer questions about these tables."
            ],
            "tables": [
                {
                    "name": table_name,
                    "description": table_data.get('description', 'No description available.'),
                    "columns": [
                        {"name": col_name, "type": col_data.get('type', 'unknown')}
                        for col_name, col_data in table_data.get('columns', {}).items()
                    ]
                } for table_name, table_data in kb.items()
            ]
        }
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {e}")

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
    return description.strip().replace('"', '')

@app.post("/regenerate-knowledge-base", tags=["Database"])
async def regenerate_knowledge_base(request: RegenerateKnowledgeBaseRequest):
    """
    Regenerates the knowledge base for a given database connection string.
    This should be called when a user connects to a new database.
    Uses fast mode (no LLM calls) for quick response.
    """
    if not chatbot_agent:
        raise HTTPException(status_code=503, detail="Service is not ready.")
    
    try:
        engine = create_engine(request.connection_string)
        inspector = inspect(engine)
        
        enriched_schema = {}
        table_names = inspector.get_table_names()
        
        # Use fast mode - simple descriptions based on names (no LLM calls)
        for table_name in table_names[:20]:  # Limit to first 20 tables for speed
            print(f"Processing table: '{table_name}'...")
            # Simple description based on table name
            table_desc = table_name.replace('_', ' ').title() + " table"
            
            enriched_schema[table_name] = {
                "description": table_desc,
                "columns": {}
            }
            
            columns = inspector.get_columns(table_name)
            foreign_keys = {fk['constrained_columns'][0]: fk for fk in inspector.get_foreign_keys(table_name)}
            
            for column in columns:
                col_name = column['name']
                col_type = str(column['type'])
                # Simple description based on column name
                col_desc = col_name.replace('_', ' ').title()
                
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
                
                enriched_schema[table_name]["columns"][col_name] = column_info
        
        # Update the cache for this connection string
        knowledge_base_cache[request.connection_string] = enriched_schema
        
        return {
            "success": True,
            "message": f"Knowledge base regenerated for {len(enriched_schema)} tables (fast mode)",
            "tables": list(enriched_schema.keys())
        }
    except Exception as e:
        print(f"Error regenerating knowledge base: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to regenerate knowledge base: {str(e)}")

@app.post("/clear-old-connections", tags=["Database"])
async def clear_old_connections(request: ClearOldConnectionsRequest):
    """
    Clears old database connections from cache.
    If old_connection_string is provided in request body, only that connection is cleared.
    Otherwise, all connections except the default one are cleared.
    """
    try:
        old_connection_string = request.old_connection_string if request else None
        if old_connection_string:
            # Clear specific connection
            if old_connection_string in db_engine_cache:
                try:
                    db_engine_cache[old_connection_string].dispose()
                except:
                    pass
                del db_engine_cache[old_connection_string]
                print(f"✓ Cleared database engine for: {old_connection_string[:50]}...")
            
            if old_connection_string in knowledge_base_cache:
                del knowledge_base_cache[old_connection_string]
                print(f"✓ Cleared knowledge base for: {old_connection_string[:50]}...")
            
            return {
                "success": True,
                "message": f"Cleared old connection: {old_connection_string[:50]}...",
                "remaining_connections": len(db_engine_cache)
            }
        else:
            # Clear all connections (keep only the default if it exists)
            default_url = os.environ.get("DATABASE_URL")
            cleared_count = 0
            
            connections_to_clear = list(db_engine_cache.keys())
            for conn_str in connections_to_clear:
                # Don't clear the default connection
                if conn_str != default_url:
                    try:
                        db_engine_cache[conn_str].dispose()
                    except:
                        pass
                    del db_engine_cache[conn_str]
                    if conn_str in knowledge_base_cache:
                        del knowledge_base_cache[conn_str]
                    cleared_count += 1
            
            print(f"✓ Cleared {cleared_count} old database connections")
            return {
                "success": True,
                "message": f"Cleared {cleared_count} old connections",
                "remaining_connections": len(db_engine_cache)
            }
    except Exception as e:
        print(f"Error clearing old connections: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to clear old connections: {str(e)}")

# To run the server: uvicorn main:app --reload
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)