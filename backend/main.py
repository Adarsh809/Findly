from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlmodel import Session, select
from backend.database import create_db_and_tables, get_session
from models import Product
import google.generativeai as genai
import os

# --- GEMINI RAG LOGIC ---
def generate_rag_response(query: str, products: list[Product]) -> str:
    context = ""
    for idx, p in enumerate(products, 1):
        context += f"{idx}. {p.title} - {p.price}\n   Description: {p.description[:300]}...\n\n"

    # --- UPDATED PROMPT ---
    system_instruction = """
    You are a helpful shopping assistant for Neusearch.
    
    INSTRUCTIONS:
    1. Analyze the User Query and the Available Products.
    2. If the user's query is specific (e.g., "dandruff", "sleep"), recommend the TOP 4 matching products from the list.
    3. Briefly explain WHY each of the 4 products is a good fit.
    4. CRITICAL: If the query is too vague (e.g., just "hair", "best product", "help"), DO NOT recommend random items. Instead, ask a polite CLARIFYING QUESTION.
    5. SIGNAL: If you are asking a clarifying question, start your response with the tag "[CLARIFY]".
    """

    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = f"{system_instruction}\n\nUser Query: {query}\n\nAvailable Products:\n{context}"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Gemini Generation Error: {e}")
        return "I'm having trouble thinking right now."

# --- APP SETUP ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return FileResponse('frontend/index.html')

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Neusearch Backend Ready"}

@app.get("/products")
def get_all_products(session: Session = Depends(get_session)):
    """Fetches products and cleans data safely."""
    products = session.exec(select(Product)).all()
    clean_products = []
    for p in products:
        p_dict = p.model_dump(exclude={"embedding"})
        clean_products.append(p_dict)
    return clean_products

@app.post("/chat")
def chat_endpoint(query: str, session: Session = Depends(get_session)):
    # 1. Greeting & Exit Guard
    conversational_phrases = ["hi", "hello", "hey", "good morning", "hola", "bye", "goodbye", "thanks", "thank you"]
    
    if query.lower().strip() in conversational_phrases:
        if query.lower().strip() in ["bye", "goodbye"]:
            reply = "Goodbye! 👋 If you have any questions later, feel free to ask."
        elif query.lower().strip() in ["thanks", "thank you"]:
            reply = "You're welcome! Let me know if you need anything else."
        else:
            reply = "Hello! 👋 I am your AI shopping assistant. How can I help you today? (e.g., 'I have dry hair')"
            
        return {
            "response": reply,
            "recommended_products": []
        }

    # 2. Embedding
    try:
        query_vector_result = genai.embed_content(
            model="models/text-embedding-004",
            content=query,
            task_type="retrieval_query"
        )
        query_vector = list(query_vector_result['embedding'])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Embedding Error: {e}")

    # 3. Search (Ensuring 4 items are fetched)
    products = session.exec(
        select(Product)
        .order_by(Product.embedding.l2_distance(query_vector))
        .limit(4)
    ).all()

    if not products:
        return {"response": "Sorry, I couldn't find any matching products.", "recommended_products": []}

    # 4. Generate Response
    ai_reply = generate_rag_response(query, products)

    # 5. Smart Filtering & Safe Serialization
    clean_recommendations = []
    if "[CLARIFY]" in ai_reply:
        ai_reply = ai_reply.replace("[CLARIFY]", "").strip()
        clean_recommendations = []
    else:
        for p in products:
            p_dict = p.model_dump(exclude={"embedding"})
            clean_recommendations.append(p_dict)

    return {
        "response": ai_reply,
        "recommended_products": clean_recommendations
    }