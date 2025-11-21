@echo off
echo AI Text Behind Image Application
echo ===============================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python 3.8 or higher and try again.
    pause
    exit /b 1
)

REM Run the application
echo Starting the application...
echo.
python ai_text_behind_image.py run --app advanced

REM If the application exits with an error
if %errorlevel% neq 0 (
    echo.
    echo Error: The application exited with an error.
    echo Please check the error message above.
    pause
)

exit /b