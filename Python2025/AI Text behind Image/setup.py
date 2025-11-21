import os
import sys
import subprocess
import platform
import argparse

def check_python_version():
    """Check if Python version is compatible."""
    required_version = (3, 8)
    current_version = sys.version_info
    
    if current_version < required_version:
        print(f"Error: Python {required_version[0]}.{required_version[1]} or higher is required.")
        print(f"Current version: {current_version[0]}.{current_version[1]}.{current_version[2]}")
        return False
    
    return True

def check_pip():
    """Check if pip is installed."""
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        print("Error: pip is not installed or not working properly.")
        return False

def install_requirements(cuda=False):
    """Install required packages."""
    try:
        print("Installing required packages...")
        
        # Install PyTorch with CUDA if requested and available
        if cuda:
            print("Installing PyTorch with CUDA support...")
            if platform.system() == "Windows":
                subprocess.run([
                    sys.executable, "-m", "pip", "install",
                    "torch==2.1.2", "torchvision==0.16.2", "--index-url", "https://download.pytorch.org/whl/cu118"
                ], check=True)
            else:  # Linux/MacOS
                subprocess.run([
                    sys.executable, "-m", "pip", "install",
                    "torch==2.1.2", "torchvision==0.16.2", "--index-url", "https://download.pytorch.org/whl/cu118"
                ], check=True)
        else:
            # Install CPU-only version
            print("Installing PyTorch (CPU only)...")
            subprocess.run([
                sys.executable, "-m", "pip", "install",
                "torch==2.1.2", "torchvision==0.16.2", "--index-url", "https://download.pytorch.org/whl/cpu"
            ], check=True)
        
        # Install other requirements
        print("Installing other requirements...")
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True)
        
        print("All packages installed successfully!")
        return True
    
    except subprocess.CalledProcessError as e:
        print(f"Error installing packages: {e}")
        return False

def create_virtual_environment(env_name="venv"):
    """Create a virtual environment."""
    try:
        print(f"Creating virtual environment: {env_name}")
        subprocess.run([sys.executable, "-m", "venv", env_name], check=True)
        
        # Determine the path to the Python executable in the virtual environment
        if platform.system() == "Windows":
            python_path = os.path.join(env_name, "Scripts", "python.exe")
        else:  # Linux/MacOS
            python_path = os.path.join(env_name, "bin", "python")
        
        print(f"Virtual environment created at: {os.path.abspath(env_name)}")
        print(f"Activate it with:")
        
        if platform.system() == "Windows":
            print(f"    {env_name}\\Scripts\\activate")
        else:  # Linux/MacOS
            print(f"    source {env_name}/bin/activate")
        
        return python_path
    
    except subprocess.CalledProcessError as e:
        print(f"Error creating virtual environment: {e}")
        return None

def setup(use_venv=True, use_cuda=False, venv_name="venv"):
    """Set up the application."""
    # Check Python version
    if not check_python_version():
        return False
    
    # Check pip
    if not check_pip():
        return False
    
    # Create virtual environment if requested
    python_executable = sys.executable
    if use_venv:
        python_executable = create_virtual_environment(venv_name)
        if not python_executable:
            return False
    
    # Install requirements
    if use_venv:
        # We need to run pip from the virtual environment
        if platform.system() == "Windows":
            pip_executable = os.path.join(os.path.dirname(python_executable), "pip.exe")
        else:  # Linux/MacOS
            pip_executable = os.path.join(os.path.dirname(python_executable), "pip")
        
        try:
            print("Installing required packages in virtual environment...")
            
            # Install PyTorch with CUDA if requested and available
            if use_cuda:
                print("Installing PyTorch with CUDA support...")
                subprocess.run([
                    pip_executable, "install",
                    "torch==2.1.2", "torchvision==0.16.2", "--index-url", "https://download.pytorch.org/whl/cu118"
                ], check=True)
            else:
                # Install CPU-only version
                print("Installing PyTorch (CPU only)...")
                subprocess.run([
                    pip_executable, "install",
                    "torch==2.1.2", "torchvision==0.16.2", "--index-url", "https://download.pytorch.org/whl/cpu"
                ], check=True)
            
            # Install other requirements
            print("Installing other requirements...")
            subprocess.run([
                pip_executable, "install", "-r", "requirements.txt"
            ], check=True)
            
            print("All packages installed successfully!")
        
        except subprocess.CalledProcessError as e:
            print(f"Error installing packages in virtual environment: {e}")
            return False
    else:
        # Install directly in the current Python environment
        if not install_requirements(use_cuda):
            return False
    
    print("\nSetup completed successfully!")
    print("You can now run the application with:")
    
    if use_venv:
        if platform.system() == "Windows":
            print(f"    {venv_name}\\Scripts\\activate")
            print("    python run_app.py")
        else:  # Linux/MacOS
            print(f"    source {venv_name}/bin/activate")
            print("    python run_app.py")
    else:
        print("    python run_app.py")
    
    return True

def main():
    parser = argparse.ArgumentParser(description="Set up AI Text Behind Image application")
    
    parser.add_argument("--no-venv", action="store_true", help="Don't create a virtual environment")
    parser.add_argument("--cuda", action="store_true", help="Install PyTorch with CUDA support")
    parser.add_argument("--venv-name", default="venv", help="Name of the virtual environment to create")
    
    args = parser.parse_args()
    
    # Run setup
    setup(use_venv=not args.no_venv, use_cuda=args.cuda, venv_name=args.venv_name)

if __name__ == "__main__":
    main()