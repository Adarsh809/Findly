from typing import Optional, List
from sqlmodel import SQLModel, Field, Column
from pgvector.sqlalchemy import Vector

class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    title: str
    price: str
    description: str
    features: str
    image_url: str
    category: str
    product_url: str  
    
    # GEMINI: text-embedding-004 uses 768 dimensions
    embedding: List[float] = Field(sa_column=Column(Vector(768)))

    class Config:
        arbitrary_types_allowed = True