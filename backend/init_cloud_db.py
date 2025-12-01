from sqlmodel import SQLModel, create_engine, text
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is missing! Check your .env file.")

# 1. Fix the Protocol (postgres:// -> postgresql://)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

try:
    # 2. THE FIX: Force SSL Mode for Cloud Connection
    engine = create_engine(DATABASE_URL, connect_args={"sslmode": "require"})
except Exception as e:
    print(f"❌ Error creating engine: {e}")
    raise e

def init_db():
    print(f"🔌 Connecting to Cloud Database...")
    
    try:
        # 3. Enable pgvector extension
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            conn.commit()
            print("✅ Extension 'vector' enabled.")

        # 4. Create Tables
        print("🏗️  Creating Tables...")
        SQLModel.metadata.create_all(engine)
        print("✅ Tables Created Successfully!")
        
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        print("💡 Hint: Go to Render Dashboard > Your Database > Access Control")
        print("   Ensure '0.0.0.0/0' is added to allowed IPs.")

if __name__ == "__main__":
    init_db()