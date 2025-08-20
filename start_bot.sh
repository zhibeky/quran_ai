#!/bin/bash

echo "🕌 Starting Quran AI Assistant Telegram Bot..."
echo "================================================"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create a .env file with your API keys:"
    echo "cp config.env.example .env"
    echo "Then edit .env with your actual keys."
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if required files exist
if [ ! -f "quran_with_tafsir.json" ]; then
    echo "❌ Error: quran_with_tafsir.json not found!"
    echo "Please ensure all data files are in the current directory."
    exit 1
fi

# Install dependencies if needed
echo "📦 Checking dependencies..."
pip3 install -r requirements.txt

# Test the RAG system first
echo "🧪 Testing RAG system..."
python3 test_rag.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🚀 Starting Telegram bot..."
    echo "Press Ctrl+C to stop the bot"
    echo "================================================"
    python3 quran_bot.py
else
    echo "❌ RAG system test failed. Please fix the issues before starting the bot."
    exit 1
fi
