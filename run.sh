#!/bin/bash

# Agent Skills - Quick Run Script

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -q -r requirements.txt

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  Please create .env file with your OPENAI_API_KEY"
    echo "  cp .env.example .env"
    exit 1
fi

# Run the chat
python -m agent.chat
