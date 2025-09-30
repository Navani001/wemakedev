# Use the official Python 3.11 image (includes newer SQLite for ChromaDB compatibility)
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Update system packages and install required dependencies including newer SQLite
RUN apt-get update && apt-get install -y \
    sqlite3 \
    libsqlite3-dev \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements_rag.txt .

# Install requirements.txt 
RUN pip install --no-cache-dir --upgrade -r requirements_rag.txt

# Copy the current directory contents into the container at /app
COPY . .

# Create cache directory with proper permissions after pip install
RUN mkdir -p /tmp/hf_cache && chmod -R 777 /tmp/hf_cache

# Also create a backup cache directory in case /tmp has issues
RUN mkdir -p /app/hf_cache && chmod -R 777 /app/hf_cache

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash app_user
RUN chown -R app_user:app_user /app
USER app_user

# Expose the port that the app runs on
EXPOSE 7860

# Start the FastAPI app on port 7860, the default port expected by Hugging Face Spaces
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]