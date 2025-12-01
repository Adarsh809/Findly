# Findly - Neusearch AI Product Discovery Assistant

Findly is a Retrieval-Augmented Generation (RAG) powered e-commerce assistant designed to bridge the gap between abstract user intent and concrete product inventory. Unlike traditional keyword search, Findly understands natural language queries (e.g., "I have a dry scalp and need something gentle") and recommends products with reasoning, clarifying questions, and rich context.

## Live Deployment and Demo

- **Live Application:** https://findly-ow2v.onrender.com/
- **Video Walkthrough:** https://drive.google.com/file/d/1wsDw5kIvVohEvzbSQpuS313Fm0gAW_Nz/view?usp=sharing

## System Architecture

The project is architected as a containerized microservice following the RAG pattern. It decouples the ingestion pipeline (ETL) from the inference engine (API) to ensure scalability and separation of concerns.

![System Architecture](./architecture.png)

### Technology Stack

**Backend Infrastructure**
- **Language:** Python 3.10
- **Framework:** FastAPI (High-performance async API)
- **ORM:** SQLModel (SQLAlchemy wrapper for type safety)
- **Database:** PostgreSQL 17 (Hosted on Render)
- **Vector Extension:** pgvector (For high-dimensional vector storage and similarity search)

**Artificial Intelligence**
- **Reasoning Engine:** Google Gemini 2.5 Flash
- **Embedding Model:** Google text-embedding-004 (768 dimensions)

**Frontend Interface**
- **Library:** React.js (Implemented via CDN for lightweight architecture)
- **Styling:** Tailwind CSS
- **Icons:** Lucide React

**DevOps & Deployment**
- **Containerization:** Docker
- **Hosting:** Render Web Services
- **Data Pipeline:** BeautifulSoup4 and Requests

## RAG Pipeline Implementation

The core logic of the application resides in a custom-built RAG pipeline designed to handle ambiguity and conversational nuance.

### 1. Hybrid Intent Classification (The Guardrail Layer)
Before querying the vector database, the system evaluates the user's input for conversational intent.
- **Greeting/Exit Logic:** Inputs like "Hi", "Bye", or "Thanks" are intercepted by a logic layer that returns instant, zero-latency responses without consuming API credits or database resources.
- **Search Intent:** Complex queries bypass the guardrail and proceed to the embedding layer.

### 2. Vector Retrieval and Semantic Search
- **Embedding:** User queries are converted into 768-dimensional vectors using the `text-embedding-004` model.
- **Similarity Search:** The system executes a cosine similarity search (`l2_distance`) against the PostgreSQL database.
- **Retrieval:** The database returns the top 4 products that are mathematically closest to the query vector, retrieving their metadata (Title, Price, Description, Image URL).

### 3. Context Augmentation and Generation
The retrieved product data is formatted into a structured context block and injected into the System Prompt of the Large Language Model (LLM).

### 4. Reasoning and Response Generation
The LLM (Gemini 2.5 Flash) processes the user query alongside the retrieved product context. It is instructed to perform one of two actions:
- **Clarification:** If the query is too vague (e.g., "hair"), the model triggers a specific signal `[CLARIFY]`. The backend detects this signal, suppresses product cards, and returns a clarifying question to the user.
- **Recommendation:** If the intent is clear, the model generates a natural language response explaining *why* the selected products match the user's specific needs.

## Data Ingestion Pipeline (ETL)

The scraping and data preparation pipeline is critical for the quality of the search results. The `scraper.py` script performs the following operations:

1.  **Extraction:** The script iterates through the product collection pages of Traya.health to identify product links.
2.  **Enrichment:** It visits each individual product page to extract deep metadata, including full descriptions and ingredient lists, which are crucial for the embedding model to understand the product's utility.
3.  **Sanitization:** Raw price data often contains hidden accessibility text (e.g., "Regular price ₹ 951..."). A Regex-based cleaning function normalizes this into a clean format (e.g., "₹ 951").
4.  **Vectorization & Loading:** The cleaned text is tokenized and embedded. The data is then Upserted (Updated/Inserted) into the PostgreSQL database to prevent duplicate entries during subsequent runs.

## Local Development Setup

Follow these steps to run the application on your local machine.

### Prerequisites
- Python 3.10 or higher
- PostgreSQL installed and running locally
- A Google Gemini API Key

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/neusearch-assignment.git](https://github.com/YOUR_USERNAME/neusearch-assignment.git)
    cd neusearch-assignment
    ```

2.  **Initialize the environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    Create a `.env` file in the root directory with the following credentials:
    ```env
    DATABASE_URL=postgresql://postgres:password@localhost:5432/neusearch_db
    GEMINI_API_KEY=your_gemini_api_key_here
    ```

### Execution

1.  **Database Initialization:**
    This script resets the schema and enables the `pgvector` extension.
    ```bash
    python reset_db.py
    ```

2.  **Data Population:**
    Runs the scraper to fetch data and populate the vector database.
    ```bash
    python scraper.py
    ```

3.  **Start the Server:**
    Launches the FastAPI backend.
    ```bash
    python -m uvicorn main:app --reload
    ```

4.  **Access the Application:**
    Navigate to `http://127.0.0.1:8000` in your web browser.

## Engineering Challenges and Trade-offs

### 1. Numpy Serialization Compatibility
**Challenge:** The Google Generative AI library returns embeddings as NumPy arrays. FastAPI's default JSON encoder cannot serialize NumPy data types, causing the API to crash during the response phase.

**Solution:** I implemented a manual serialization middleware within the endpoint logic. This explicitly converts NumPy arrays to standard Python lists (`list(vector)`) before the response is constructed. Additionally, I configured the API to exclude the heavy raw embedding data from the frontend response payload to reduce bandwidth usage.

### 2. Handling Ambiguous Queries
**Challenge:** During testing, single-word queries like "hair" resulted in the vector search returning random hair-related products. While mathematically "correct" (they were the closest vectors), this was a poor user experience.

**Solution:** I implemented a Clarification Protocol. The system prompt was engineered to detect ambiguity and return a specific tag `[CLARIFY]`. The backend logic intercepts this tag to prevent the rendering of irrelevant product cards and instead presents the user with a follow-up question.

### 3. Frontend Architecture Selection
**Decision:** I opted for a CDN-based React architecture rather than a build-step heavy framework like Next.js or Vite.

**Rationale:** This decision aligns with the assignment's "Single File" constraint for simplicity and ease of review. It eliminates the need for a separate frontend build process in the Docker container, significantly reducing deployment complexity and build times on Render.

## Future Improvements

Given more time, I would implement the following enhancements:

1.  **Async Human-in-the-Loop (HITL):** I would add a feedback mechanism (Thumbs Up/Down) to the chat interface. Negative feedback would log the conversation query and response pair to a review database, allowing for the manual refinement of system prompts and the re-indexing of problematic products.

2.  **HNSW Indexing:** The current implementation uses a flat search (exact nearest neighbor). As the dataset scales beyond 10,000 products, I would implement Hierarchical Navigable Small World (HNSW) indexing within `pgvector` to ensure sub-millisecond query performance at scale.

3.  **Conversational Memory:** Currently, the application processes each query independently. I would integrate a Redis layer to store session-based conversation history, allowing users to ask follow-up questions such as "How much is the second one?" that reference previous context.