@echo off
title AI Business Idea Validator Server
color 0A
echo.
echo ========================================
echo    AI Business Idea Validator
echo ========================================
echo.
echo Starting Django Development Server...
echo.
echo Server will start on: http://127.0.0.1:8084/
echo.
echo Press Ctrl+C to stop the server
echo.
echo ========================================
echo.

cd /d "%~dp0"

REM Show Python version
python --version
echo.

REM Run Django server with verbose output
python manage.py runserver 127.0.0.1:8084 --verbosity=2 --settings=idea_validator.settings

echo.
echo Server stopped. Press any key to exit...
pause > nul
