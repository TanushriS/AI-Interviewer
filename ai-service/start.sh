#!/bin/bash

# Start Ollama server in the background
echo "Starting Ollama server..."
ollama serve > ollama.log 2>&1 &

# Wait for Ollama to be ready
echo "Waiting for Ollama server to start..."
while ! curl -s http://127.0.0.1:11434 >/dev/null; do
    sleep 1
done
echo "Ollama server is up!"

# Pull the models
echo "Pulling models (this may take a few minutes)..."
ollama pull deepseek-r1:1.5b
ollama pull nomic-embed-text:latest

# Start FastAPI application
echo "Starting FastAPI app..."
python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
