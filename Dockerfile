# 1. Base Image: Use a lightweight Python version
FROM python:3.10-slim

# 2. Set environment variables to ensure Python output is sent to logs immediately
ENV PYTHONUNBUFFERED=1

# 3. Set the working directory inside the container
WORKDIR /app

# 4. Copy requirements first (Optimization: Docker layers cache this step)
COPY requirements.txt .

# 5. Install dependencies
# We use --no-cache-dir to keep the image small
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the rest of the application code (Includes frontend folder!)
COPY . .

# 7. Expose the port Render uses (Standard is 10000)
EXPOSE 10000

# 8. Start the application
# We use shell format to properly expand the $PORT variable
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000}"]