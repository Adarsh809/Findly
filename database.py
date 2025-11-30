from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv
import os

# 1. Load secrets
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL .env file me nahi mili!")

# 2. Connection Engine
engine = create_engine(DATABASE_URL, echo=False)

# 3. Create Tables Function
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# 4. Session Dependency
def get_session():
    with Session(engine) as session:
        yield session