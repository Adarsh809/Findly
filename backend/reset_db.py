from sqlmodel import SQLModel
from backend.database import engine  # <--- FIXED: Import from database.py
from models import Product   # Keep this to ensure models are registered

def reset_database():
    print("🗑️  Deleting old tables...")
    SQLModel.metadata.drop_all(engine)
    
    print("🆕 Creating new tables with correct Vector(768)...")
    SQLModel.metadata.create_all(engine)
    
    print("✅ Database Reset Complete! You are ready for Gemini.")

if __name__ == "__main__":
    reset_database()