#!/usr/bin/env python3

import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_component_tests(verbose=False):
    """Run component tests."""
    if not os.path.exists("test_components.py"):
        print("Error: test_components.py not found.")
        return False
    
    print("Running component tests...")
    try:
        cmd = [sys.executable, "test_components.py"]
        if verbose:
            subprocess.check_call(cmd)
        else:
            subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        print("✅ Component tests passed.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Component tests failed: {e}")
        return False

def run_quick_test(verbose=False):
    """Run a quick test with a sample image."""
    if not os.path.exists("quick_test.py"):
        print("Error: quick_test.py not found.")
        return False
    
    print("Running quick test...")
    try:
        cmd = [sys.executable, "quick_test.py"]
        if verbose:
            subprocess.check_call(cmd)
        else:
            subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        print("✅ Quick test passed.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Quick test failed: {e}")
        return False

def run_model_tests(verbose=False):
    """Test AI models."""
    if not os.path.exists("model_manager.py"):
        print("Error: model_manager.py not found.")
        return False
    
    print("Testing AI models...")
    try:
        cmd = [sys.executable, "model_manager.py", "test"]
        if verbose:
            subprocess.check_call(cmd)
        else:
            subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        print("✅ Model tests passed.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Model tests failed: {e}")
        return False

def run_examples_test(verbose=False):
    """Run examples test."""
    if not os.path.exists("examples.py"):
        print("Error: examples.py not found.")
        return False
    
    # Find a sample image
    sample_dir = Path("sample_images")
    if not sample_dir.exists():
        print("Error: sample_images directory not found.")
        print("Downloading sample images...")
        try:
            subprocess.check_call([sys.executable, "sample_images.py", "--num", "1"])
        except subprocess.CalledProcessError as e:
            print(f"Error downloading sample images: {e}")
            return False
    
    # Find the first image in the sample_images directory
    image_path = None
    if sample_dir.exists():
        for ext in [".jpg", ".jpeg", ".png"]:
            images = list(sample_dir.glob(f"*{ext}"))
            if images:
                image_path = str(images[0])
                break
    
    if image_path is None:
        print("Error: No sample images found.")
        return False
    
    print("Running examples test...")
    try:
        cmd = [sys.executable, "examples.py", "--image", image_path, "--basic"]
        if verbose:
            subprocess.check_call(cmd)
        else:
            subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        print("✅ Examples test passed.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Examples test failed: {e}")
        return False

def run_all_tests(verbose=False):
    """Run all tests."""
    results = {
        "component_tests": run_component_tests(verbose),
        "quick_test": run_quick_test(verbose),
        "model_tests": run_model_tests(verbose),
        "examples_test": run_examples_test(verbose)
    }
    
    # Print summary
    print("\nTest Summary:")
    for test_name, result in results.items():
        status = "✅ Passed" if result else "❌ Failed"
        print(f"{test_name}: {status}")
    
    # Overall result
    if all(results.values()):
        print("\n✅ All tests passed!")
        return True
    else:
        print("\n❌ Some tests failed.")
        return False

def main():
    parser = argparse.ArgumentParser(description="Run tests for AI Text Behind Image")
    parser.add_argument("--component", action="store_true", help="Run component tests")
    parser.add_argument("--quick", action="store_true", help="Run quick test")
    parser.add_argument("--model", action="store_true", help="Test AI models")
    parser.add_argument("--examples", action="store_true", help="Run examples test")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--verbose", action="store_true", help="Show verbose output")
    args = parser.parse_args()
    
    # If no specific test is requested, run all tests
    if not (args.component or args.quick or args.model or args.examples or args.all):
        args.all = True
    
    # Run the requested tests
    if args.all:
        success = run_all_tests(args.verbose)
    else:
        success = True
        if args.component:
            success = run_component_tests(args.verbose) and success
        if args.quick:
            success = run_quick_test(args.verbose) and success
        if args.model:
            success = run_model_tests(args.verbose) and success
        if args.examples:
            success = run_examples_test(args.verbose) and success
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())