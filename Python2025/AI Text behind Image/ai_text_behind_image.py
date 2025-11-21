#!/usr/bin/env python3

import os
import sys
import argparse
import subprocess
import webbrowser
import time

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

def run_app(app_type="advanced", port=8501, open_browser=True):
    """Run the Streamlit application."""
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

def download_sample_images():
    """Download sample images for testing."""
    if not os.path.exists("sample_images.py"):
        print("Error: sample_images.py not found.")
        return False
    
    print("Downloading sample images...")
    try:
        subprocess.check_call([sys.executable, "sample_images.py"])
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error downloading sample images: {e}")
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
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error downloading models: {e}")
        return False

def run_examples(image_path, text="Hello World"):
    """Run example scripts."""
    if not os.path.exists("examples.py"):
        print("Error: examples.py not found.")
        return False
    
    print("Running examples...")
    try:
        subprocess.check_call([sys.executable, "examples.py", "--image", image_path, "--text", text])
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running examples: {e}")
        return False

def run_benchmark(image_paths):
    """Run benchmark tests."""
    if not os.path.exists("benchmark.py"):
        print("Error: benchmark.py not found.")
        return False
    
    print("Running benchmark...")
    try:
        cmd = [sys.executable, "benchmark.py", "--images"] + image_paths
        subprocess.check_call(cmd)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running benchmark: {e}")
        return False

def run_batch_processing(input_dir, output_dir, text="Hello World"):
    """Run batch processing."""
    if not os.path.exists("batch_processor.py"):
        print("Error: batch_processor.py not found.")
        return False
    
    print("Running batch processing...")
    try:
        subprocess.check_call([sys.executable, "batch_processor.py", "--input-dir", input_dir, "--output-dir", output_dir, "--text", text])
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running batch processing: {e}")
        return False

def run_cli(input_path, output_path, text="Hello World"):
    """Run the command-line interface."""
    if not os.path.exists("cli.py"):
        print("Error: cli.py not found.")
        return False
    
    print("Running CLI...")
    try:
        subprocess.check_call([sys.executable, "cli.py", "--input", input_path, "--output", output_path, "--text", text])
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running CLI: {e}")
        return False

def create_font_catalog():
    """Create a catalog of available fonts."""
    if not os.path.exists("font_utils.py"):
        print("Error: font_utils.py not found.")
        return False
    
    print("Creating font catalog...")
    try:
        subprocess.check_call([sys.executable, "font_utils.py", "--catalog"])
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error creating font catalog: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="AI Text Behind Image - Main Interface")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Run app command
    run_parser = subparsers.add_parser("run", help="Run the application")
    run_parser.add_argument("--app", choices=["basic", "advanced", "demo"], default="advanced", help="Application type")
    run_parser.add_argument("--port", type=int, default=8501, help="Port to run on")
    run_parser.add_argument("--no-browser", action="store_true", help="Don't open browser")
    
    # Download samples command
    samples_parser = subparsers.add_parser("samples", help="Download sample images")
    
    # Download models command
    models_parser = subparsers.add_parser("models", help="Download AI models")
    
    # Examples command
    examples_parser = subparsers.add_parser("examples", help="Run example scripts")
    examples_parser.add_argument("--image", required=True, help="Input image path")
    examples_parser.add_argument("--text", default="Hello World", help="Text to insert")
    
    # Benchmark command
    benchmark_parser = subparsers.add_parser("benchmark", help="Run benchmark tests")
    benchmark_parser.add_argument("--images", nargs="+", required=True, help="Input image paths")
    
    # Batch command
    batch_parser = subparsers.add_parser("batch", help="Run batch processing")
    batch_parser.add_argument("--input-dir", required=True, help="Input directory")
    batch_parser.add_argument("--output-dir", required=True, help="Output directory")
    batch_parser.add_argument("--text", default="Hello World", help="Text to insert")
    
    # CLI command
    cli_parser = subparsers.add_parser("cli", help="Run command-line interface")
    cli_parser.add_argument("--input", required=True, help="Input image path")
    cli_parser.add_argument("--output", required=True, help="Output image path")
    cli_parser.add_argument("--text", default="Hello World", help="Text to insert")
    
    # Fonts command
    fonts_parser = subparsers.add_parser("fonts", help="Create font catalog")
    
    args = parser.parse_args()
    
    # Check environment
    if not check_environment():
        return 1
    
    # Run the specified command
    if args.command == "run":
        run_app(args.app, args.port, not args.no_browser)
    
    elif args.command == "samples":
        download_sample_images()
    
    elif args.command == "models":
        download_models()
    
    elif args.command == "examples":
        run_examples(args.image, args.text)
    
    elif args.command == "benchmark":
        run_benchmark(args.images)
    
    elif args.command == "batch":
        run_batch_processing(args.input_dir, args.output_dir, args.text)
    
    elif args.command == "cli":
        run_cli(args.input, args.output, args.text)
    
    elif args.command == "fonts":
        create_font_catalog()
    
    else:
        # If no command is specified, run the advanced app
        run_app()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())