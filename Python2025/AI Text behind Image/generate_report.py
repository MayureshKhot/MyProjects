#!/usr/bin/env python3

import os
import sys
import platform
import subprocess
import datetime
import json
import argparse
from pathlib import Path

def get_system_info():
    """Get system information."""
    info = {
        "os": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor()
        },
        "python": {
            "version": platform.python_version(),
            "implementation": platform.python_implementation(),
            "compiler": platform.python_compiler(),
            "build": platform.python_build()
        }
    }
    
    return info

def get_installed_packages():
    """Get installed Python packages."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--format=json"],
            capture_output=True,
            text=True
        )
        packages = json.loads(result.stdout)
        return packages
    except Exception as e:
        print(f"Error getting installed packages: {e}")
        return []

def get_gpu_info():
    """Get GPU information."""
    gpu_info = {}
    
    try:
        # Try to get CUDA information from PyTorch
        import torch
        gpu_info["cuda_available"] = torch.cuda.is_available()
        if torch.cuda.is_available():
            gpu_info["cuda_version"] = torch.version.cuda
            gpu_info["device_count"] = torch.cuda.device_count()
            gpu_info["device_name"] = torch.cuda.get_device_name(0)
            gpu_info["device_capability"] = torch.cuda.get_device_capability(0)
    except ImportError:
        gpu_info["cuda_available"] = False
    
    return gpu_info

def get_application_info():
    """Get application information."""
    info = {
        "files": [],
        "version": "Unknown"
    }
    
    # Get all Python files
    for file_path in Path(".").glob("*.py"):
        if file_path.is_file():
            info["files"].append({
                "name": file_path.name,
                "size": file_path.stat().st_size,
                "modified": datetime.datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            })
    
    # Try to get version from git
    try:
        result = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
        if result.returncode == 0:
            info["version"] = result.stdout.strip()
    except Exception:
        pass
    
    return info

def get_model_info():
    """Get information about downloaded models."""
    if not os.path.exists("model_manager.py"):
        return {"error": "model_manager.py not found"}
    
    try:
        result = subprocess.run(
            [sys.executable, "model_manager.py", "list", "--json"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return {"error": "Could not parse model information"}
        else:
            return {"error": result.stderr}
    except Exception as e:
        return {"error": str(e)}

def generate_report(output_path=None, format="text"):
    """Generate a comprehensive report."""
    # Get the current timestamp
    timestamp = datetime.datetime.now().isoformat()
    
    # Collect information
    report = {
        "timestamp": timestamp,
        "system": get_system_info(),
        "packages": get_installed_packages(),
        "gpu": get_gpu_info(),
        "application": get_application_info(),
        "models": get_model_info()
    }
    
    # Set default output path if not provided
    if output_path is None:
        output_dir = Path("reports")
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}"
    
    # Write the report
    if format == "json":
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)
    else:  # text format
        with open(output_path, "w") as f:
            f.write("AI Text Behind Image - System Report\n")
            f.write("=====================================\n\n")
            f.write(f"Generated: {timestamp}\n\n")
            
            f.write("System Information:\n")
            f.write(f"  OS: {report['system']['os']['system']} {report['system']['os']['release']} {report['system']['os']['version']}\n")
            f.write(f"  Machine: {report['system']['os']['machine']}\n")
            f.write(f"  Processor: {report['system']['os']['processor']}\n\n")
            
            f.write("Python Information:\n")
            f.write(f"  Version: {report['system']['python']['version']}\n")
            f.write(f"  Implementation: {report['system']['python']['implementation']}\n")
            f.write(f"  Compiler: {report['system']['python']['compiler']}\n\n")
            
            f.write("GPU Information:\n")
            if report['gpu'].get('cuda_available', False):
                f.write(f"  CUDA Available: Yes\n")
                f.write(f"  CUDA Version: {report['gpu'].get('cuda_version', 'Unknown')}\n")
                f.write(f"  Device Count: {report['gpu'].get('device_count', 0)}\n")
                f.write(f"  Device Name: {report['gpu'].get('device_name', 'Unknown')}\n\n")
            else:
                f.write("  CUDA Available: No\n\n")
            
            f.write("Application Information:\n")
            f.write(f"  Version: {report['application']['version']}\n")
            f.write(f"  Files: {len(report['application']['files'])}\n\n")
            
            f.write("Installed Packages:\n")
            for package in report['packages']:
                f.write(f"  {package['name']} {package['version']}\n")
            f.write("\n")
            
            f.write("Downloaded Models:\n")
            if isinstance(report['models'], dict) and 'error' in report['models']:
                f.write(f"  Error: {report['models']['error']}\n")
            elif isinstance(report['models'], list):
                for model in report['models']:
                    f.write(f"  {model.get('name', 'Unknown')} ({model.get('type', 'Unknown')})\n")
            else:
                f.write("  No models found\n")
    
    print(f"Report generated and saved to: {output_path}")
    return output_path

def main():
    parser = argparse.ArgumentParser(description="Generate a comprehensive report about the system and application")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    args = parser.parse_args()
    
    generate_report(args.output, args.format)
    return 0

if __name__ == "__main__":
    sys.exit(main())