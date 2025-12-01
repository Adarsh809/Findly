# 1. Base Image
FROM python:3.10-slim

# 2. Set environment variables
ENV PYTHONUNBUFFERED=1
# Add the current directory to Python path so it can find the 'backend' module
ENV PYTHONPATH=/app

# 3. Set the working directory
WORKDIR /app

# 4. Copy requirements
COPY requirements.txt .

# 5. Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# --- THE FIX ---
# Do NOT flatten. Copy the folder AS a folder.
# This creates /app/backend/ inside the container
COPY backend/ backend/

# Copy frontend as well
COPY frontend/ frontend/

# 6. Expose port
EXPOSE 10000

# 7. Start the app pointing to the backend module
# Notice the change: 'backend.main:app' instead of just 'main:app'
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-10000}"]