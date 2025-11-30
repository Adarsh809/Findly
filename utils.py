import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# 1. Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("⚠️ Warning: GEMINI_API_KEY missing in .env")

genai.configure(api_key=api_key)

def get_embedding(text: str) -> list[float]:
    """
    Generates a 768-dimension vector using Gemini.
    """
    if not text:
        return []

    text = text.replace("\n", " ").strip()

    try:
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=text,
            task_type="retrieval_document",
            title="Product"
        )
        # CRITICAL FIX: Convert Numpy array to standard Python list
        return list(result['embedding'])
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return []