#!/usr/bin/env python3

import os
import sys
import shutil
import argparse
from pathlib import Path

def cleanup_temp_files():
    """Clean up temporary files created by the application."""
    temp_dirs = [
        ".streamlit",  # Streamlit cache
        "__pycache__",  # Python cache
        ".pytest_cache",  # Pytest cache
        "output"  # Output directory
    ]
    
    # Find all temporary directories
    removed = 0
    for temp_dir in temp_dirs:
        if os.path.exists(temp_dir):
            print(f"Removing {temp_dir}...")
            try:
                shutil.rmtree(temp_dir)
                removed += 1
            except Exception as e:
                print(f"Error removing {temp_dir}: {e}")
    
    # Find all __pycache__ directories recursively
    for root, dirs, files in os.walk("."):
        for dir_name in dirs:
            if dir_name == "__pycache__":
                cache_dir = os.path.join(root, dir_name)
                print(f"Removing {cache_dir}...")
                try:
                    shutil.rmtree(cache_dir)
                    removed += 1
                except Exception as e:
                    print(f"Error removing {cache_dir}: {e}")
    
    # Find all .pyc files
    for root, dirs, files in os.walk("."):
        for file_name in files:
            if file_name.endswith(".pyc"):
                pyc_file = os.path.join(root, file_name)
                print(f"Removing {pyc_file}...")
                try:
                    os.remove(pyc_file)
                    removed += 1
                except Exception as e:
                    print(f"Error removing {pyc_file}: {e}")
    
    return removed

def cleanup_model_cache(keep_models=False):
    """Clean up model cache."""
    # Check if the model cache directory exists
    cache_dir = os.path.expanduser("~/.cache/huggingface")
    if os.path.exists(cache_dir) and not keep_models:
        print(f"Removing model cache at {cache_dir}...")
        try:
            shutil.rmtree(cache_dir)
            return 1
        except Exception as e:
            print(f"Error removing model cache: {e}")
    
    return 0

def cleanup_output_files():
    """Clean up output files."""
    output_dir = Path("output")
    if output_dir.exists():
        print(f"Removing output directory...")
        try:
            shutil.rmtree(output_dir)
            return 1
        except Exception as e:
            print(f"Error removing output directory: {e}")
    
    return 0

def main():
    parser = argparse.ArgumentParser(description="Cleanup utility for AI Text Behind Image")
    parser.add_argument("--all", action="store_true", help="Clean up everything (temp files, model cache, output files)")
    parser.add_argument("--temp", action="store_true", help="Clean up temporary files")
    parser.add_argument("--models", action="store_true", help="Clean up model cache")
    parser.add_argument("--output", action="store_true", help="Clean up output files")
    parser.add_argument("--keep-models", action="store_true", help="Keep downloaded models when cleaning up")
    args = parser.parse_args()
    
    # If no specific cleanup is requested, clean up temporary files by default
    if not (args.all or args.temp or args.models or args.output):
        args.temp = True
    
    total_removed = 0
    
    # Clean up temporary files
    if args.all or args.temp:
        removed = cleanup_temp_files()
        total_removed += removed
        print(f"Removed {removed} temporary files/directories.")
    
    # Clean up model cache
    if args.all or args.models:
        removed = cleanup_model_cache(args.keep_models)
        total_removed += removed
        if removed > 0:
            print("Removed model cache.")
        elif args.keep_models:
            print("Kept model cache as requested.")
    
    # Clean up output files
    if args.all or args.output:
        removed = cleanup_output_files()
        total_removed += removed
        if removed > 0:
            print("Removed output files.")
    
    print(f"\nCleanup completed. Removed {total_removed} items in total.")
    return 0

if __name__ == "__main__":
    sys.exit(main())