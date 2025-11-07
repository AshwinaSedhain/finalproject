# demo.py
"""
Demonstration script for the Data-Aware AI Chatbot.
"""
import uuid
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
import os

load_dotenv()
from chatbot.agent import ChatbotAgent

def main():
    print("\n" + "="*70); print(" 🧠 Welcome to the Data-Aware AI Chatbot Demo 🧠"); print("="*70)

    try:
        chatbot = ChatbotAgent()
        if not chatbot.knowledge_base:
            # Agent will print a more specific error, so we can just exit.
            return
    except Exception as e:
        print(f"\n❌ Critical Error during Agent initialization: {e}"); return

    print("\nConnecting to the database for query execution...")
    try:
        db_url = os.environ.get("DATABASE_URL")
        if not db_url: raise ValueError("DATABASE_URL not found in .env file.")
        engine = create_engine(db_url)
        # Test connection
        with engine.connect() as connection:
            print("✓ Database connection for query execution is successful.")
    except Exception as e:
        print(f"\n❌ Database connection failed: {e}"); return

    def execute_query(sql: str) -> pd.DataFrame:
        try: return pd.read_sql(sql, engine)
        except Exception as e: raise Exception(f"Database execution error: {e}")

    user_id = str(uuid.uuid4())
    
    print("\n" + "─"*70)
    print(f"✅ Ready to chat! Your session ID is: {user_id}")
    print("   Type `/schema` to see what I know, or just ask a question!")
    print("─"*70)
    
    while True:
        try:
            question = input("\n👤 You: ").strip()
            if question.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!"); break
            if not question: continue
            
            print("🤖 AI is thinking...", end='\r', flush=True)
            
            # The call is now simpler: no need to pass the schema.
            result = chatbot.process(
                user_prompt=question,
                user_id=user_id,
                execute_query=execute_query
            )
            
            print(" " * 20, end='\r')
            print(f"🤖 AI: {result['response']}")

            if result.get('from_cache'): print("   ⚡ (Served from cache)")
            if result.get('visualization'):
                filename = "demo_chart.html"
                result['visualization'].write_html(filename)
                print(f"   📊 Chart saved to '{filename}'.")
        except KeyboardInterrupt:
            print("\n\n👋 Session interrupted. Goodbye!"); break
        except Exception as e:
            print(f"\n❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()