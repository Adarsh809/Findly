# 1. Base Image
FROM python:3.10-slim

# 2. Set environment variables
ENV PYTHONUNBUFFERED=1

# --- THE FIX ---
# We add '/app/backend' to the path so Python finds models.py, utils.py, etc.
ENV PYTHONPATH=/app:/app/backend

# 3. Set the working directory
WORKDIR /app

# 4. Copy requirements
COPY requirements.txt .

# 5. Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy folders structure properly
COPY backend/ backend/
COPY frontend/ frontend/

# 7. Expose port
EXPOSE 10000

# 8. Start the app
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-10000}"]