import os
import sys
import argparse
import subprocess
import platform
import webbrowser
import time

def check_environment():
    """Check if the environment is properly set up."""
    # Check if Python is installed
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required.")
        return False
    
    # Check if pip is installed
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "--version"], 
                             stdout=subprocess.DEVNULL, 
                             stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        print("Error: pip is not installed or not working properly.")
        return False
    
    # Check if required packages are installed
    required_packages = ["streamlit", "pillow", "numpy", "opencv-python", "torch"]
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing required packages: {', '.join(missing_packages)}")
        print("Please run 'pip install -r requirements.txt' to install them.")
        return False
    
    return True

def install_requirements():
    """Install required packages."""
    print("Installing required packages...")
    
    # Check if requirements.txt exists
    if not os.path.exists("requirements.txt"):
        print("Error: requirements.txt not found.")
        return False
    
    # Install packages
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Required packages installed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing packages: {e}")
        return False

def download_sample_images():
    """Download sample images for testing."""
    if not os.path.exists("sample_images"):
        print("Downloading sample images...")
        try:
            subprocess.check_call([sys.executable, "sample_images.py", "--count", "3"])
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error downloading sample images: {e}")
            return False
    else:
        print("Sample images already downloaded.")
        return True

def start_application(app_type="advanced", port=8501, open_browser=True):
    """Start the Streamlit application."""
    # Determine which app to run
    if app_type == "basic":
        app_file = "app.py"
    elif app_type == "advanced":
        app_file = "advanced_app.py"
    elif app_type == "demo":
        app_file = "demo.py"
    else:
        print(f"Error: Unknown app type '{app_type}'")
        return False
    
    # Check if the app file exists
    if not os.path.exists(app_file):
        print(f"Error: {app_file} not found.")
        return False
    
    # Start the application
    print(f"Starting {app_type} application on port {port}...")
    
    # Build the command
    cmd = [sys.executable, "-m", "streamlit", "run", app_file, "--server.port", str(port)]
    
    # Start the process
    process = subprocess.Popen(cmd)
    
    # Wait for the server to start
    time.sleep(3)
    
    # Open the browser
    if open_browser:
        url = f"http://localhost:{port}"
        print(f"Opening {url} in your browser...")
        webbrowser.open(url)
    
    print(f"Application is running at http://localhost:{port}")
    print("Press Ctrl+C to stop the application.")
    
    try:
        # Wait for the process to finish
        process.wait()
        return True
    except KeyboardInterrupt:
        # Stop the process
        process.terminate()
        print("Application stopped.")
        return True
    except Exception as e:
        print(f"Error running application: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Start the AI Text Behind Image application")
    
    parser.add_argument("--app", choices=["basic", "advanced", "demo"], default="advanced",
                        help="Which application to run (default: advanced)")
    parser.add_argument("--port", type=int, default=8501,
                        help="Port to run the application on (default: 8501)")
    parser.add_argument("--no-browser", action="store_true",
                        help="Don't open the browser automatically")
    parser.add_argument("--install", action="store_true",
                        help="Install required packages")
    parser.add_argument("--download-samples", action="store_true",
                        help="Download sample images")
    
    args = parser.parse_args()
    
    # Check environment
    if not check_environment():
        if args.install:
            if not install_requirements():
                return 1
        else:
            print("Use --install to install required packages.")
            return 1
    
    # Download sample images if requested
    if args.download_samples:
        if not download_sample_images():
            return 1
    
    # Start the application
    if not start_application(args.app, args.port, not args.no_browser):
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())