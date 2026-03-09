#!/bin/bash

# HouseBets Quick Start Script

echo "🎲 HouseBets - Setting up your prediction market bot..."
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Create virtual environment (optional but recommended)
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
else
    echo "✅ Using existing virtual environment..."
    source venv/bin/activate
fi

# Check if .env exists and has BOT_TOKEN
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Please create a .env file with your BOT_TOKEN"
    exit 1
fi

if ! grep -q "BOT_TOKEN=your_discord_bot_token_here" .env; then
    echo "✅ Bot token appears to be configured"
else
    echo "⚠️  Warning: BOT_TOKEN still has default value"
    echo "Please update your .env file with your actual Discord bot token"
    echo ""
    read -p "Press Enter to continue anyway or Ctrl+C to exit..."
fi

echo ""
echo "🚀 Starting HouseBets bot..."
echo "Press Ctrl+C to stop"
echo ""

python3 main.py
