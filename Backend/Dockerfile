FROM python:3.10-slim

WORKDIR /app

# Install system dependencies (minimal, safe)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy rest of the project
COPY . .

# Expose Render port
EXPOSE 10000

# Run Flask app
CMD ["python", "app.py"]



