#!/bin/bash

echo "==================================================="
echo "AI Text Behind Image - Installation Script"
echo "==================================================="
echo 

# Check Python installation
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH."
    echo "Please install Python 3.8 or higher from your package manager"
    echo "or from https://www.python.org/downloads/"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d" " -f2)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo "Error: Python 3.8 or higher is required."
    echo "Current version: $PYTHON_VERSION"
    exit 1
fi

echo "Python $PYTHON_VERSION detected."

# Check pip installation
echo "Checking pip installation..."
if ! python3 -m pip --version &> /dev/null; then
    echo "Error: pip is not installed or not working properly."
    echo "Please install pip or fix your Python installation."
    exit 1
fi

echo "pip is installed."

# Ask user if they want to create a virtual environment
read -p "Do you want to create a virtual environment? (y/n): " CREATE_VENV

if [[ "$CREATE_VENV" =~ ^[Yy]$ ]]; then
    echo "Creating virtual environment..."
    
    # Check if venv module is available
    if ! python3 -c "import venv" &> /dev/null; then
        echo "Error: venv module is not available."
        echo "Please install it using: pip install virtualenv"
        exit 1
    fi
    
    # Create virtual environment
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment."
        exit 1
    fi
    
    echo "Virtual environment created."
    
    # Activate virtual environment
    echo "Activating virtual environment..."
    source venv/bin/activate
    if [ $? -ne 0 ]; then
        echo "Error: Failed to activate virtual environment."
        exit 1
    fi
    
    echo "Virtual environment activated."
    
    # Use python instead of python3 in virtual environment
    PYTHON_CMD="python"
else
    PYTHON_CMD="python3"
fi

# Detect system
OS=$(uname -s)
if [ "$OS" = "Darwin" ]; then
    SYSTEM="macos"
else
    SYSTEM="linux"
fi

# Ask user if they want to install CUDA-enabled PyTorch
if [ "$SYSTEM" = "linux" ]; then
    read -p "Do you want to install CUDA-enabled PyTorch? (y/n): " INSTALL_CUDA
else
    # macOS doesn't support CUDA
    INSTALL_CUDA="n"
fi

# Install requirements
echo "Installing required packages..."

if [[ "$INSTALL_CUDA" =~ ^[Yy]$ ]]; then
    echo "Installing PyTorch with CUDA support..."
    $PYTHON_CMD -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install PyTorch with CUDA support."
        exit 1
    fi
    
    # Install other requirements excluding PyTorch
    $PYTHON_CMD -m pip install -r requirements.txt --ignore-installed torch torchvision torchaudio
else
    # Install all requirements
    $PYTHON_CMD -m pip install -r requirements.txt
fi

if [ $? -ne 0 ]; then
    echo "Error: Failed to install required packages."
    exit 1
fi

echo "Required packages installed successfully."

# Ask user if they want to download sample images
read -p "Do you want to download sample images? (y/n): " DOWNLOAD_SAMPLES

if [[ "$DOWNLOAD_SAMPLES" =~ ^[Yy]$ ]]; then
    echo "Downloading sample images..."
    $PYTHON_CMD sample_images.py
    if [ $? -ne 0 ]; then
        echo "Error: Failed to download sample images."
        exit 1
    fi
    
    echo "Sample images downloaded successfully."
fi

# Ask user if they want to download AI models
read -p "Do you want to download AI models now? (y/n): " DOWNLOAD_MODELS

if [[ "$DOWNLOAD_MODELS" =~ ^[Yy]$ ]]; then
    echo "Downloading AI models..."
    $PYTHON_CMD model_manager.py download --type depth --name Intel/dpt-large
    $PYTHON_CMD model_manager.py download --type segmentation --name deeplabv3_resnet101
    
    echo "AI models downloaded successfully."
fi

echo 
echo "==================================================="
echo "Installation completed successfully!"
echo "==================================================="
echo 
echo "To run the application, use one of the following commands:"
echo 
echo "  $PYTHON_CMD start.py --app basic     (Basic version)"
echo "  $PYTHON_CMD start.py --app advanced  (Advanced version)"
echo "  $PYTHON_CMD start.py --app demo      (Demo version)"
echo 
echo "Or simply run: $PYTHON_CMD start.py"
echo 

# Make the script executable
chmod +x start.py

# If using virtual environment, remind user to activate it
if [[ "$CREATE_VENV" =~ ^[Yy]$ ]]; then
    echo "Remember to activate the virtual environment before running the application:"
    echo "  source venv/bin/activate"
fi