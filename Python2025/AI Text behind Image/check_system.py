#!/usr/bin/env python3

import os
import sys
import platform
import subprocess
import importlib.util

def check_python_version():
    """Check if Python version is 3.8 or higher."""
    required_version = (3, 8)
    current_version = sys.version_info
    
    if current_version >= required_version:
        print(f"✅ Python version: {platform.python_version()} (Required: 3.8+)")
        return True
    else:
        print(f"❌ Python version: {platform.python_version()} (Required: 3.8+)")
        return False

def check_pip():
    """Check if pip is installed."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "--version"], 
                             stdout=subprocess.DEVNULL, 
                             stderr=subprocess.DEVNULL)
        print("✅ pip is installed")
        return True
    except subprocess.CalledProcessError:
        print("❌ pip is not installed")
        return False

def check_package(package_name):
    """Check if a package is installed."""
    spec = importlib.util.find_spec(package_name.replace("-", "_"))
    if spec is not None:
        try:
            module = importlib.import_module(package_name.replace("-", "_"))
            version = getattr(module, "__version__", "unknown")
            print(f"✅ {package_name} is installed (version: {version})")
            return True
        except ImportError:
            print(f"✅ {package_name} is installed (version: unknown)")
            return True
    else:
        print(f"❌ {package_name} is not installed")
        return False

def check_cuda():
    """Check if CUDA is available (if PyTorch is installed)."""
    try:
        import torch
        if torch.cuda.is_available():
            print(f"✅ CUDA is available (version: {torch.version.cuda})")
            print(f"   GPU: {torch.cuda.get_device_name(0)}")
            return True
        else:
            print("ℹ️ CUDA is not available (CPU mode will be used)")
            return False
    except ImportError:
        print("ℹ️ PyTorch is not installed, cannot check CUDA availability")
        return False

def check_disk_space(required_mb=1000):
    """Check if there's enough disk space (default: 1GB)."""
    # Get the current directory
    current_dir = os.getcwd()
    
    # Check available disk space
    if platform.system() == "Windows":
        import ctypes
        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(current_dir), None, None, ctypes.pointer(free_bytes))
        free_mb = free_bytes.value / (1024 * 1024)
    else:  # Unix/Linux/MacOS
        stat = os.statvfs(current_dir)
        free_mb = (stat.f_bavail * stat.f_frsize) / (1024 * 1024)
    
    if free_mb >= required_mb:
        print(f"✅ Disk space: {free_mb:.2f} MB available (Required: {required_mb} MB)")
        return True
    else:
        print(f"❌ Disk space: {free_mb:.2f} MB available (Required: {required_mb} MB)")
        return False

def main():
    print("System Requirements Check for AI Text Behind Image")
    print("==================================================")
    print(f"Operating System: {platform.system()} {platform.release()}")
    print()
    
    # Check Python version
    python_ok = check_python_version()
    
    # Check pip
    pip_ok = check_pip()
    
    # Check required packages
    print("\nChecking required packages:")
    packages = ["streamlit", "pillow", "numpy", "opencv-python", "torch", "torchvision", "transformers"]
    packages_ok = all(check_package(package) for package in packages)
    
    # Check CUDA
    print("\nChecking CUDA availability:")
    cuda_ok = check_cuda()
    
    # Check disk space
    print("\nChecking disk space:")
    disk_ok = check_disk_space(1000)  # Require at least 1GB
    
    # Summary
    print("\nSummary:")
    if python_ok and pip_ok and packages_ok and disk_ok:
        print("✅ Your system meets all the requirements!")
        print("   You can run the application with:")
        if platform.system() == "Windows":
            print("   python ai_text_behind_image.py run")
            print("   or double-click on run_app.bat")
        else:
            print("   python3 ai_text_behind_image.py run")
            print("   or ./run_app.sh (after making it executable with chmod +x run_app.sh)")
    else:
        print("❌ Your system does not meet all the requirements.")
        print("   Please fix the issues above before running the application.")
        if not python_ok:
            print("   - Install Python 3.8 or higher")
        if not pip_ok:
            print("   - Install pip")
        if not packages_ok:
            print("   - Install missing packages with: pip install -r requirements.txt")
        if not disk_ok:
            print("   - Free up some disk space")
    
    # Additional information
    print("\nAdditional Information:")
    if not cuda_ok and platform.system() != "Darwin":  # Not on macOS
        print("ℹ️ CUDA is not available. The application will run in CPU mode, which may be slower.")
        print("   If you have an NVIDIA GPU, consider installing CUDA for better performance.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())