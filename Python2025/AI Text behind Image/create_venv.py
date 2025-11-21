#!/usr/bin/env python3

import os
import sys
import subprocess
import argparse
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8 or higher."""
    required_version = (3, 8)
    current_version = sys.version_info
    
    if current_version < required_version:
        print(f"Error: Python {required_version[0]}.{required_version[1]} or higher is required.")
        print(f"Current version: {current_version[0]}.{current_version[1]}.{current_version[2]}")
        return False
    
    print(f"Python version: {current_version[0]}.{current_version[1]}.{current_version[2]}")
    return True

def create_virtual_environment(venv_path, force=False):
    """Create a virtual environment."""
    venv_path = Path(venv_path)
    
    # Check if virtual environment already exists
    if venv_path.exists() and not force:
        print(f"Virtual environment already exists at {venv_path}")
        response = input("Do you want to recreate it? (y/n): ").strip().lower()
        if response != "y":
            print("Using existing virtual environment.")
            return True
        print("Recreating virtual environment...")
    
    # Create virtual environment
    try:
        if venv_path.exists() and force:
            import shutil
            shutil.rmtree(venv_path)
        
        print(f"Creating virtual environment at {venv_path}...")
        subprocess.check_call([sys.executable, "-m", "venv", str(venv_path)])
        print("Virtual environment created successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error creating virtual environment: {e}")
        return False

def install_dependencies(venv_path, dev=False):
    """Install dependencies in the virtual environment."""
    venv_path = Path(venv_path)
    
    # Check if virtual environment exists
    if not venv_path.exists():
        print(f"Error: Virtual environment not found at {venv_path}")
        return False
    
    # Determine pip path
    if sys.platform == "win32":
        pip_path = venv_path / "Scripts" / "pip"
    else:
        pip_path = venv_path / "bin" / "pip"
    
    # Install dependencies
    try:
        print("Installing dependencies...")
        subprocess.check_call([str(pip_path), "install", "-U", "pip"])
        subprocess.check_call([str(pip_path), "install", "-r", "requirements.txt"])
        
        if dev:
            print("Installing development dependencies...")
            subprocess.check_call([str(pip_path), "install", "-r", "dev-requirements.txt"])
        
        print("Dependencies installed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        return False

def create_activation_scripts(venv_path):
    """Create activation scripts for the virtual environment."""
    venv_path = Path(venv_path)
    
    # Check if virtual environment exists
    if not venv_path.exists():
        print(f"Error: Virtual environment not found at {venv_path}")
        return False
    
    # Create activation script for Windows
    if sys.platform == "win32":
        activate_bat = Path("activate_venv.bat")
        with open(activate_bat, "w") as f:
            f.write(f"@echo off\n")
            f.write(f"echo Activating virtual environment...\n")
            f.write(f"call \"{venv_path / 'Scripts' / 'activate'}\"\n")
            f.write(f"echo Virtual environment activated.\n")
            f.write(f"cmd /k\n")
        print(f"Created activation script: {activate_bat}")
    
    # Create activation script for Linux/macOS
    else:
        activate_sh = Path("activate_venv.sh")
        with open(activate_sh, "w") as f:
            f.write(f"#!/bin/bash\n")
            f.write(f"echo Activating virtual environment...\n")
            f.write(f"source \"{venv_path / 'bin' / 'activate'}\"\n")
            f.write(f"echo Virtual environment activated.\n")
            f.write(f"exec $SHELL\n")
        
        # Make the script executable
        os.chmod(activate_sh, 0o755)
        print(f"Created activation script: {activate_sh}")
    
    return True

def main():
    parser = argparse.ArgumentParser(description="Create a virtual environment for AI Text Behind Image")
    parser.add_argument("--path", default="venv", help="Path to create the virtual environment (default: venv)")
    parser.add_argument("--force", action="store_true", help="Force recreation of the virtual environment")
    parser.add_argument("--dev", action="store_true", help="Install development dependencies")
    args = parser.parse_args()
    
    print("AI Text Behind Image - Virtual Environment Setup")
    print("============================================")
    print()
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Create virtual environment
    if not create_virtual_environment(args.path, args.force):
        return 1
    
    # Install dependencies
    if not install_dependencies(args.path, args.dev):
        return 1
    
    # Create activation scripts
    if not create_activation_scripts(args.path):
        return 1
    
    print("\nVirtual environment setup completed successfully.")
    print("\nTo activate the virtual environment:")
    
    if sys.platform == "win32":
        print("  Run: activate_venv.bat")
    else:
        print("  Run: source activate_venv.sh")
    
    print("\nAfter activation, you can run the application:")
    print("  python ai_text_behind_image.py run --app advanced")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())