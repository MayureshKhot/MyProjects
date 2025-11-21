#!/usr/bin/env python3

import os
import sys
import shutil
import argparse
import subprocess
from pathlib import Path

def uninstall_packages():
    """Uninstall Python packages installed by the application."""
    packages = [
        "streamlit",
        "pillow",
        "numpy",
        "opencv-python",
        "torch",
        "torchvision",
        "transformers",
        "matplotlib",
        "requests",
        "python-dotenv",
        "timm",
        "huggingface-hub",
        "scipy",
        "freetype-py",
        "streamlit-webrtc"
    ]
    
    print("Uninstalling Python packages...")
    for package in packages:
        try:
            print(f"Uninstalling {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "-y", package])
        except subprocess.CalledProcessError as e:
            print(f"Error uninstalling {package}: {e}")
    
    print("Python packages uninstalled.")
    return True

def remove_model_cache():
    """Remove model cache."""
    cache_dir = os.path.expanduser("~/.cache/huggingface")
    if os.path.exists(cache_dir):
        print(f"Removing model cache at {cache_dir}...")
        try:
            shutil.rmtree(cache_dir)
            print("Model cache removed.")
            return True
        except Exception as e:
            print(f"Error removing model cache: {e}")
            return False
    else:
        print("Model cache not found.")
        return True

def remove_sample_images():
    """Remove sample images."""
    sample_dir = Path("sample_images")
    if sample_dir.exists():
        print("Removing sample images...")
        try:
            shutil.rmtree(sample_dir)
            print("Sample images removed.")
            return True
        except Exception as e:
            print(f"Error removing sample images: {e}")
            return False
    else:
        print("Sample images not found.")
        return True

def remove_output_files():
    """Remove output files."""
    output_dir = Path("output")
    if output_dir.exists():
        print("Removing output files...")
        try:
            shutil.rmtree(output_dir)
            print("Output files removed.")
            return True
        except Exception as e:
            print(f"Error removing output files: {e}")
            return False
    else:
        print("Output files not found.")
        return True

def remove_cache_files():
    """Remove cache files."""
    cache_dirs = [
        ".streamlit",
        "__pycache__",
        ".pytest_cache"
    ]
    
    print("Removing cache files...")
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            try:
                shutil.rmtree(cache_dir)
                print(f"{cache_dir} removed.")
            except Exception as e:
                print(f"Error removing {cache_dir}: {e}")
    
    # Find all __pycache__ directories recursively
    for root, dirs, files in os.walk("."):
        for dir_name in dirs:
            if dir_name == "__pycache__":
                cache_dir = os.path.join(root, dir_name)
                try:
                    shutil.rmtree(cache_dir)
                    print(f"{cache_dir} removed.")
                except Exception as e:
                    print(f"Error removing {cache_dir}: {e}")
    
    # Find all .pyc files
    for root, dirs, files in os.walk("."):
        for file_name in files:
            if file_name.endswith(".pyc"):
                pyc_file = os.path.join(root, file_name)
                try:
                    os.remove(pyc_file)
                    print(f"{pyc_file} removed.")
                except Exception as e:
                    print(f"Error removing {pyc_file}: {e}")
    
    print("Cache files removed.")
    return True

def main():
    parser = argparse.ArgumentParser(description="Uninstall AI Text Behind Image")
    parser.add_argument("--all", action="store_true", help="Remove everything (packages, models, samples, output, cache)")
    parser.add_argument("--packages", action="store_true", help="Uninstall Python packages")
    parser.add_argument("--models", action="store_true", help="Remove model cache")
    parser.add_argument("--samples", action="store_true", help="Remove sample images")
    parser.add_argument("--output", action="store_true", help="Remove output files")
    parser.add_argument("--cache", action="store_true", help="Remove cache files")
    parser.add_argument("--yes", action="store_true", help="Skip confirmation")
    args = parser.parse_args()
    
    # If no specific action is requested, show help
    if not (args.all or args.packages or args.models or args.samples or args.output or args.cache):
        parser.print_help()
        return 0
    
    print("AI Text Behind Image - Uninstall Utility")
    print("=======================================")
    print()
    
    # Confirm uninstallation
    if not args.yes:
        print("WARNING: This will remove the selected components of the application.")
        print("This action cannot be undone.")
        print()
        response = input("Do you want to continue? (y/n): ").strip().lower()
        if response != "y":
            print("Uninstallation cancelled.")
            return 0
    
    # Uninstall packages
    if args.all or args.packages:
        uninstall_packages()
    
    # Remove model cache
    if args.all or args.models:
        remove_model_cache()
    
    # Remove sample images
    if args.all or args.samples:
        remove_sample_images()
    
    # Remove output files
    if args.all or args.output:
        remove_output_files()
    
    # Remove cache files
    if args.all or args.cache:
        remove_cache_files()
    
    print("\nUninstallation completed.")
    return 0

if __name__ == "__main__":
    sys.exit(main())