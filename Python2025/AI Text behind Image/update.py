#!/usr/bin/env python3

import os
import sys
import subprocess
import argparse
from pathlib import Path

def check_git():
    """Check if git is installed and the repository is a git repository."""
    try:
        # Check if git is installed
        subprocess.check_call(["git", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Check if the current directory is a git repository
        subprocess.check_call(["git", "rev-parse", "--is-inside-work-tree"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        return True
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        return False

def get_current_version():
    """Get the current version of the application."""
    if not check_git():
        return "Unknown"
    
    try:
        # Get the latest commit hash
        result = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
        commit_hash = result.stdout.strip()
        
        # Get the latest tag if available
        result = subprocess.run(["git", "describe", "--tags", "--abbrev=0"], capture_output=True, text=True)
        if result.returncode == 0:
            tag = result.stdout.strip()
            return f"{tag} ({commit_hash})"
        else:
            return commit_hash
    except subprocess.CalledProcessError:
        return "Unknown"

def check_for_updates():
    """Check if there are updates available."""
    if not check_git():
        print("Error: This is not a git repository or git is not installed.")
        return False
    
    try:
        # Fetch the latest changes
        print("Fetching the latest changes...")
        subprocess.check_call(["git", "fetch"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Check if there are updates available
        result = subprocess.run(["git", "rev-list", "HEAD..origin/main", "--count"], capture_output=True, text=True)
        updates_count = int(result.stdout.strip())
        
        if updates_count > 0:
            print(f"Updates available: {updates_count} new commit(s)")
            return True
        else:
            print("No updates available. You are already on the latest version.")
            return False
    except subprocess.CalledProcessError as e:
        print(f"Error checking for updates: {e}")
        return False

def update_application(backup=True):
    """Update the application to the latest version."""
    if not check_git():
        print("Error: This is not a git repository or git is not installed.")
        return False
    
    # Create a backup if requested
    if backup:
        backup_dir = Path("backup")
        backup_dir.mkdir(exist_ok=True)
        
        # Get the current timestamp
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create a backup of the current code
        print(f"Creating backup in {backup_dir}...")
        for ext in [".py", ".md", ".txt", ".bat", ".sh"]:
            for file_path in Path(".").glob(f"*{ext}"):
                if file_path.is_file():
                    backup_file = backup_dir / f"{file_path.stem}_{timestamp}{file_path.suffix}"
                    try:
                        import shutil
                        shutil.copy2(file_path, backup_file)
                    except Exception as e:
                        print(f"Error creating backup of {file_path}: {e}")
    
    try:
        # Pull the latest changes
        print("Updating to the latest version...")
        subprocess.check_call(["git", "pull", "origin", "main"])
        
        # Update dependencies
        print("Updating dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--upgrade"])
        
        print("\nUpdate completed successfully!")
        print(f"Current version: {get_current_version()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error updating the application: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Update utility for AI Text Behind Image")
    parser.add_argument("--check", action="store_true", help="Check for updates without installing them")
    parser.add_argument("--no-backup", action="store_true", help="Skip creating a backup before updating")
    args = parser.parse_args()
    
    print("AI Text Behind Image - Update Utility")
    print("=====================================")
    print(f"Current version: {get_current_version()}")
    print()
    
    if args.check:
        # Only check for updates
        check_for_updates()
    else:
        # Check for updates and install them if available
        if check_for_updates():
            print()
            response = input("Do you want to update to the latest version? (y/n): ").strip().lower()
            if response == "y":
                update_application(not args.no_backup)
        else:
            # No updates available
            pass
    
    return 0

if __name__ == "__main__":
    sys.exit(main())