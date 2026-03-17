@echo off
echo Starting AI Business Idea Validator Server...
echo.
echo Please try these URLs in your browser:
echo http://localhost:5555/
echo http://127.0.0.1:5555/
echo.
echo Press Ctrl+C to stop the server
echo.
cd /d "%~dp0"
python manage.py runserver 0.0.0.0:5555 --debug
pause
