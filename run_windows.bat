@echo off
setlocal

echo ============================================
echo   Mongo CRUD (Django + MongoDB) - Setup
echo ============================================

REM Go to the folder this .bat file lives in
cd /d "%~dp0"

REM 1. Create venv if it doesn't exist
if not exist "venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo.
        echo [ERROR] Could not create a virtual environment.
        echo Make sure Python 3 is installed and on your PATH ^(https://python.org^).
        pause
        exit /b 1
    )
)

REM 2. Activate venv
call venv\Scripts\activate.bat

REM 3. Install/upgrade dependencies
echo.
echo Installing dependencies from requirements.txt ...
pip install --upgrade pip >nul
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo [ERROR] pip install failed. Check your internet connection and try again.
    pause
    exit /b 1
)

REM 4. Run Django migrations (for auth/admin/sessions in SQLite only)
echo.
echo Running migrations...
python manage.py migrate

REM 5. Reminder about MongoDB
echo.
echo ------------------------------------------------------------
echo Make sure MongoDB is running before continuing:
echo   - Local install: mongod should be running on localhost:27017
echo   - Or Docker:      docker run -d -p 27017:27017 --name mongo mongo:7
echo   - Or Atlas:       set MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/mydb
echo ------------------------------------------------------------
echo.
pause

REM 6. Run the dev server
echo Starting server at http://127.0.0.1:8000/
start "" http://127.0.0.1:8000/
python manage.py runserver

pause
