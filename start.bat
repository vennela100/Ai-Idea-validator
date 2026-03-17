@echo off
REM AI Business Idea Validator - Windows Startup Script

echo 🚀 Starting AI Business Idea Validator...

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📚 Installing dependencies...
pip install -r requirements.txt

REM Check environment file
if not exist ".env" (
    echo ⚠️  .env file not found. Creating from .env.example...
    copy .env.example .env
    echo 📝 Please edit .env file with your settings before running the app.
)

REM Run database migrations
echo 🗄️  Running database migrations...
python manage.py makemigrations
python manage.py migrate

REM Collect static files
echo 📁 Collecting static files...
python manage.py collectstatic --noinput

REM Start the development server
echo 🌐 Starting development server...
echo 📍 Application will be available at: http://127.0.0.1:8000/
echo 🔧 Admin panel available at: http://127.0.0.1:8000/admin/
echo 📊 API available at: http://127.0.0.1:8000/api/
echo.
echo Press Ctrl+C to stop the server
echo.

python manage.py runserver
