#!/bin/bash

echo "AI Text Behind Image Application"
echo "==============================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH."
    echo "Please install Python 3.8 or higher and try again."
    exit 1
fi

# Run the application
echo "Starting the application..."
echo ""
python3 ai_text_behind_image.py run --app advanced

# If the application exits with an error
if [ $? -ne 0 ]; then
    echo ""
    echo "Error: The application exited with an error."
    echo "Please check the error message above."
fi