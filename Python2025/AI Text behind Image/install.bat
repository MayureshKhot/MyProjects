@echo off
setlocal enabledelayedexpansion

echo ===================================================
echo AI Text Behind Image - Installation Script
echo ===================================================
echo.

:: Check Python installation
echo Checking Python installation...
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python 3.8 or higher from https://www.python.org/downloads/
    echo and make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

:: Check Python version
for /f "tokens=2" %%a in ('python --version 2^>^&1') do set PYTHON_VERSION=%%a
for /f "tokens=1,2 delims=." %%a in ("!PYTHON_VERSION!") do (
    set PYTHON_MAJOR=%%a
    set PYTHON_MINOR=%%b
)

if !PYTHON_MAJOR! lss 3 (
    echo Error: Python 3.8 or higher is required.
    echo Current version: !PYTHON_VERSION!
    pause
    exit /b 1
)

if !PYTHON_MAJOR! equ 3 if !PYTHON_MINOR! lss 8 (
    echo Error: Python 3.8 or higher is required.
    echo Current version: !PYTHON_VERSION!
    pause
    exit /b 1
)

echo Python !PYTHON_VERSION! detected.

:: Check pip installation
echo Checking pip installation...
python -m pip --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Error: pip is not installed or not working properly.
    echo Please install pip or fix your Python installation.
    pause
    exit /b 1
)

echo pip is installed.

:: Ask user if they want to create a virtual environment
set /p CREATE_VENV=Do you want to create a virtual environment? (y/n): 

if /i "!CREATE_VENV!"=="y" (
    echo Creating virtual environment...
    
    :: Check if venv module is available
    python -c "import venv" > nul 2>&1
    if %errorlevel% neq 0 (
        echo Error: venv module is not available.
        echo Please install it using: pip install virtualenv
        pause
        exit /b 1
    )
    
    :: Create virtual environment
    python -m venv venv
    if %errorlevel% neq 0 (
        echo Error: Failed to create virtual environment.
        pause
        exit /b 1
    )
    
    echo Virtual environment created.
    
    :: Activate virtual environment
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
    if %errorlevel% neq 0 (
        echo Error: Failed to activate virtual environment.
        pause
        exit /b 1
    )
    
    echo Virtual environment activated.
)

:: Ask user if they want to install CUDA-enabled PyTorch
set /p INSTALL_CUDA=Do you want to install CUDA-enabled PyTorch? (y/n): 

:: Install requirements
echo Installing required packages...

if /i "!INSTALL_CUDA!"=="y" (
    echo Installing PyTorch with CUDA support...
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
    if %errorlevel% neq 0 (
        echo Error: Failed to install PyTorch with CUDA support.
        pause
        exit /b 1
    )
    
    :: Install other requirements excluding PyTorch
    pip install -r requirements.txt --ignore-installed torch torchvision torchaudio
) else (
    :: Install all requirements
    pip install -r requirements.txt
)

if %errorlevel% neq 0 (
    echo Error: Failed to install required packages.
    pause
    exit /b 1
)

echo Required packages installed successfully.

:: Ask user if they want to download sample images
set /p DOWNLOAD_SAMPLES=Do you want to download sample images? (y/n): 

if /i "!DOWNLOAD_SAMPLES!"=="y" (
    echo Downloading sample images...
    python sample_images.py
    if %errorlevel% neq 0 (
        echo Error: Failed to download sample images.
        pause
        exit /b 1
    )
    
    echo Sample images downloaded successfully.
)

:: Ask user if they want to download AI models
set /p DOWNLOAD_MODELS=Do you want to download AI models now? (y/n): 

if /i "!DOWNLOAD_MODELS!"=="y" (
    echo Downloading AI models...
    python model_manager.py download --type depth --name Intel/dpt-large
    python model_manager.py download --type segmentation --name deeplabv3_resnet101
    
    echo AI models downloaded successfully.
)

echo.
echo ===================================================
echo Installation completed successfully!
echo ===================================================
echo.
echo To run the application, use one of the following commands:
echo.
echo   python start.py --app basic     (Basic version)
echo   python start.py --app advanced  (Advanced version)
echo   python start.py --app demo      (Demo version)
echo.
echo Or simply run: python start.py
echo.

pause