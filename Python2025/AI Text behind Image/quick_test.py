#!/usr/bin/env python3

import os
import sys
import argparse
import subprocess
from pathlib import Path

def download_sample_image():
    """Download a sample image if not already available."""
    # Check if sample_images.py exists
    if not os.path.exists("sample_images.py"):
        print("Error: sample_images.py not found.")
        return None
    
    # Check if sample_images directory exists
    sample_dir = Path("sample_images")
    if not sample_dir.exists():
        print("Downloading sample images...")
        try:
            subprocess.check_call([sys.executable, "sample_images.py", "--num", "1"])
        except subprocess.CalledProcessError as e:
            print(f"Error downloading sample images: {e}")
            return None
    
    # Find the first image in the sample_images directory
    if sample_dir.exists():
        for ext in [".jpg", ".jpeg", ".png"]:
            images = list(sample_dir.glob(f"*{ext}"))
            if images:
                return str(images[0])
    
    print("No sample images found.")
    return None

def download_models():
    """Download required AI models if not already available."""
    if not os.path.exists("model_manager.py"):
        print("Error: model_manager.py not found.")
        return False
    
    print("Checking AI models...")
    try:
        # Check if models are already downloaded
        result = subprocess.run(
            [sys.executable, "model_manager.py", "list"],
            capture_output=True,
            text=True
        )
        
        # If models are not downloaded, download them
        if "Intel/dpt-large" not in result.stdout:
            print("Downloading depth model...")
            subprocess.check_call([sys.executable, "model_manager.py", "download", "--type", "depth", "--name", "Intel/dpt-large"])
        
        if "deeplabv3_resnet101" not in result.stdout:
            print("Downloading segmentation model...")
            subprocess.check_call([sys.executable, "model_manager.py", "download", "--type", "segmentation", "--name", "deeplabv3_resnet101"])
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error downloading models: {e}")
        return False

def run_test(image_path, text="Hello World", output_path=None):
    """Run a quick test with the provided image."""
    if not os.path.exists("cli.py"):
        print("Error: cli.py not found.")
        return False
    
    # Set default output path if not provided
    if output_path is None:
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        output_path = str(output_dir / "quick_test_result.png")
    
    print(f"Processing image: {image_path}")
    print(f"Text: {text}")
    print(f"Output will be saved to: {output_path}")
    
    try:
        # Run the CLI to process the image
        subprocess.check_call([
            sys.executable, "cli.py",
            image_path,
            output_path,
            text,
            "--show-depth",  # Save depth map for visualization
            "--perspective", "0.5",  # Add some perspective effect
            "--shadow", "0.5"  # Add some shadow effect
        ])
        
        # Verify the output file was actually created
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            print(f"\nTest completed successfully!")
            print(f"Result saved to: {output_path}")
            
            # Try to open the result image
            try:
                if sys.platform == "win32":
                    os.startfile(output_path)
                elif sys.platform == "darwin":  # macOS
                    subprocess.call(["open", output_path])
                else:  # Linux
                    subprocess.call(["xdg-open", output_path])
            except Exception as e:
                print(f"Could not open the result image automatically: {e}")
            
            return True
        else:
            print(f"Error: Output file was not created or is empty.")
            return False
    except subprocess.CalledProcessError as e:
        print(f"Error processing image: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error during test: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Quick test for AI Text Behind Image")
    parser.add_argument("--image", help="Path to input image (if not provided, a sample image will be downloaded)")
    parser.add_argument("--text", default="Hello World", help="Text to insert into the image")
    parser.add_argument("--output", help="Path to save the output image")
    args = parser.parse_args()
    
    # Check if the image path is provided
    image_path = args.image
    if image_path is None:
        print("No image path provided, downloading a sample image...")
        image_path = download_sample_image()
        if image_path is None:
            print("Could not download or find a sample image.")
            return 1
    
    # Download models if needed
    if not download_models():
        print("Could not download required AI models.")
        return 1
    
    # Run the test
    if not run_test(image_path, args.text, args.output):
        print("Test failed.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())