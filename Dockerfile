# 1. Base Image
FROM python:3.10-slim

# 2. Set environment variables
ENV PYTHONUNBUFFERED=1

# 3. Set the working directory inside the container
WORKDIR /app

# 4. Copy requirements (This stays in the root folder)
COPY requirements.txt .

# 5. Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# --- THE MAGIC PART ---
# Instead of copying ".", we copy specific folders to flatten the structure.

# 6. Copy the contents of the 'backend' folder to the container's root
# This puts main.py, models.py, etc. right inside /app/
COPY backend/ .

# 7. Copy the 'frontend' folder to /app/frontend/
# This ensures FileResponse('frontend/index.html') still works
COPY frontend/ frontend/

# 8. Expose port
EXPOSE 10000

# 9. Start the app
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000}"]