#!/usr/bin/env python3

import os
import sys
import subprocess
import argparse
import webbrowser
import time
import shutil
from pathlib import Path

def check_environment():
    """Check if the environment is properly set up."""
    # Check if Python is installed
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required.")
        return False
    
    # Check if required packages are installed
    # Map package names to their import names
    package_import_map = {
        "streamlit": "streamlit",
        "pillow": "PIL",  # Pillow is imported as PIL
        "numpy": "numpy",
        "opencv-python": "cv2",  # opencv-python is imported as cv2
        "torch": "torch"
    }
    
    missing_packages = []
    
    for package, import_name in package_import_map.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing required packages: {', '.join(missing_packages)}")
        print("Please run 'pip install -r requirements.txt' to install them.")
        return False
    
    return True

def install_dependencies():
    """Install required dependencies."""
    print("Installing required dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        print("Please try running 'pip install --user -r requirements.txt' manually.")
        return False

def download_sample_images():
    """Download sample images for testing."""
    if not os.path.exists("sample_images.py"):
        print("Error: sample_images.py not found.")
        return False
    
    print("Downloading sample images...")
    try:
        subprocess.check_call([sys.executable, "sample_images.py"])
        print("✅ Sample images downloaded successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error downloading sample images: {e}")
        return False

def download_models():
    """Download AI models."""
    if not os.path.exists("model_manager.py"):
        print("Error: model_manager.py not found.")
        return False
    
    print("Downloading AI models...")
    try:
        # Download depth model
        subprocess.check_call([sys.executable, "model_manager.py", "download", "--type", "depth", "--name", "Intel/dpt-large"])
        
        # Download segmentation model
        subprocess.check_call([sys.executable, "model_manager.py", "download", "--type", "segmentation", "--name", "deeplabv3_resnet101"])
        
        print("✅ AI models downloaded successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error downloading models: {e}")
        return False

def run_quick_test():
    """Run a quick test to verify the application is working."""
    if not os.path.exists("quick_test.py"):
        print("Error: quick_test.py not found.")
        return False
    
    print("Running a quick test...")
    try:
        subprocess.check_call([sys.executable, "quick_test.py"])
        print("✅ Quick test completed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running quick test: {e}")
        return False

def run_application(app_type="advanced", port=8501):
    """Run the application."""
    if not os.path.exists("ai_text_behind_image.py"):
        print("Error: ai_text_behind_image.py not found.")
        return False
    
    print(f"Starting the {app_type} application...")
    try:
        # Start the application
        process = subprocess.Popen(
            [sys.executable, "ai_text_behind_image.py", "run", "--app", app_type, "--port", str(port)]
        )
        
        # Wait for the application to start
        time.sleep(3)
        
        # Open the browser
        url = f"http://localhost:{port}"
        print(f"Opening {url} in your browser...")
        webbrowser.open(url)
        
        print(f"\nThe application is running at {url}")
        print("Press Ctrl+C to stop the application.")
        
        # Wait for the user to press Ctrl+C
        try:
            process.wait()
        except KeyboardInterrupt:
            process.terminate()
            print("\nApplication stopped.")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting the application: {e}")
        return False

def create_env_file():
    """Create a .env file for API keys."""
    if os.path.exists(".env"):
        print(".env file already exists.")
        return True
    
    if not os.path.exists(".env.example"):
        print("Error: .env.example not found.")
        return False
    
    print("Creating .env file for API keys...")
    try:
        shutil.copy(".env.example", ".env")
        print("✅ .env file created successfully.")
        print("Please edit the .env file to add your API keys.")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Get started with AI Text Behind Image")
    parser.add_argument("--skip-dependencies", action="store_true", help="Skip installing dependencies")
    parser.add_argument("--skip-samples", action="store_true", help="Skip downloading sample images")
    parser.add_argument("--skip-models", action="store_true", help="Skip downloading AI models")
    parser.add_argument("--skip-test", action="store_true", help="Skip running a quick test")
    parser.add_argument("--app", choices=["basic", "advanced", "demo"], default="advanced", help="Application type to run")
    parser.add_argument("--port", type=int, default=8501, help="Port to run the application on")
    args = parser.parse_args()
    
    print("AI Text Behind Image - Getting Started")
    print("=====================================")
    print()
    
    # Check environment
    if not check_environment():
        if not args.skip_dependencies:
            print("\nAttempting to install dependencies...")
            if not install_dependencies():
                print("\nPlease install the required dependencies manually and try again.")
                return 1
        else:
            print("\nPlease install the required dependencies manually and try again.")
            return 1
    
    # Download sample images
    if not args.skip_samples:
        print()
        download_sample_images()
    
    # Download AI models
    if not args.skip_models:
        print()
        download_models()
    
    # Run a quick test
    if not args.skip_test:
        print()
        run_quick_test()
    
    # Create .env file
    print()
    create_env_file()
    
    # Run the application
    print()
    run_application(args.app, args.port)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())