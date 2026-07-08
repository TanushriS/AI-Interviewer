FROM python:3.10-slim

# Install system dependencies (only ffmpeg is required for audio processing)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements and install python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY main.py .

# Copy and configure the start script
COPY start.sh .
RUN chmod +x start.sh

# Expose FastAPI port
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["./start.sh"]
