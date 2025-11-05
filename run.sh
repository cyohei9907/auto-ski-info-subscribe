#!/bin/bash
# Startup script for the crawler service

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    echo "Please copy .env.example to .env and configure it."
    exit 1
fi

# Create logs directory
mkdir -p logs

# Start the service
echo "Starting Social Media Crawler Service..."
python app.py
