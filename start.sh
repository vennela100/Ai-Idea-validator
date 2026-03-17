#!/bin/bash

# AI Business Idea Validator - Startup Script

echo "🚀 Starting AI Business Idea Validator..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check environment file
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "📝 Please edit .env file with your settings before running the app."
fi

# Run database migrations
echo "🗄️  Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Start the development server
echo "🌐 Starting development server..."
echo "📍 Application will be available at: http://127.0.0.1:8000/"
echo "🔧 Admin panel available at: http://127.0.0.1:8000/admin/"
echo "📊 API available at: http://127.0.0.1:8000/api/"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python manage.py runserver
