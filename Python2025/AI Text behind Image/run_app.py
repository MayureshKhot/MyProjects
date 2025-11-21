import os
import sys
import argparse
import subprocess

def run_streamlit_app(app_file="app.py", port=8501):
    """Run the Streamlit app with the specified file and port."""
    try:
        # Check if the app file exists
        if not os.path.isfile(app_file):
            print(f"Error: App file '{app_file}' does not exist.")
            return False
        
        # Run the Streamlit app
        print(f"Starting Streamlit app: {app_file} on port {port}")
        subprocess.run([
            "streamlit", "run", app_file,
            "--server.port", str(port),
            "--server.headless", "true",
            "--browser.serverAddress", "localhost",
            "--theme.primaryColor", "#FF4B4B",
            "--theme.backgroundColor", "#0E1117",
            "--theme.secondaryBackgroundColor", "#262730",
            "--theme.textColor", "#FAFAFA"
        ])
        
        return True
    
    except Exception as e:
        print(f"Error running Streamlit app: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Run AI Text Behind Image Streamlit App")
    
    parser.add_argument("--app", choices=["basic", "advanced", "demo"], default="advanced",
                        help="Which app to run (basic, advanced, or demo)")
    parser.add_argument("--port", type=int, default=8501, help="Port to run the Streamlit app on")
    
    args = parser.parse_args()
    
    # Determine which app file to run
    if args.app == "basic":
        app_file = "app.py"
    elif args.app == "advanced":
        app_file = "advanced_app.py"
    else:  # demo
        app_file = "demo.py"
    
    # Run the app
    run_streamlit_app(app_file, args.port)

if __name__ == "__main__":
    main()