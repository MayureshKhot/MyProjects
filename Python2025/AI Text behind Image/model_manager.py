import os
import sys
import argparse
import json
import shutil
import requests
import torch
from tqdm import tqdm
import hashlib

# Import local modules if available
try:
    from ai_models import ModelFactory
except ImportError:
    pass

# Define model information
MODEL_INFO = {
    "depth": {
        "Intel/dpt-large": {
            "description": "High-quality depth estimation model",
            "size": "1.3 GB",
            "source": "huggingface",
            "url": "https://huggingface.co/Intel/dpt-large"
        },
        "Intel/dpt-hybrid-midas": {
            "description": "Faster depth estimation model with good quality",
            "size": "470 MB",
            "source": "huggingface",
            "url": "https://huggingface.co/Intel/dpt-hybrid-midas"
        }
    },
    "segmentation": {
        "deeplabv3_resnet101": {
            "description": "High-quality segmentation model",
            "size": "230 MB",
            "source": "torchvision",
            "url": None
        },
        "fcn_resnet101": {
            "description": "Alternative segmentation model",
            "size": "210 MB",
            "source": "torchvision",
            "url": None
        }
    }
}

# Define model cache directory
DEFAULT_CACHE_DIR = os.path.join(os.path.expanduser("~"), ".ai_text_behind_image", "models")

def get_cache_dir(cache_dir=None):
    """Get the model cache directory."""
    if cache_dir is None:
        cache_dir = DEFAULT_CACHE_DIR
    
    # Create cache directory if it doesn't exist
    os.makedirs(cache_dir, exist_ok=True)
    
    return cache_dir

def list_available_models():
    """List all available models."""
    print("Available Models:")
    print("-" * 80)
    
    for model_type, models in MODEL_INFO.items():
        print(f"\n{model_type.upper()} MODELS:")
        print("-" * 40)
        
        for model_name, info in models.items():
            print(f"  {model_name}")
            print(f"    Description: {info['description']}")
            print(f"    Size: {info['size']}")
            print(f"    Source: {info['source']}")
            if info['url']:
                print(f"    URL: {info['url']}")
            print()

def list_downloaded_models(cache_dir=None):
    """List all downloaded models."""
    cache_dir = get_cache_dir(cache_dir)
    
    # Check if cache directory exists
    if not os.path.exists(cache_dir):
        print(f"Cache directory {cache_dir} does not exist.")
        return []
    
    # Get model info file
    info_file = os.path.join(cache_dir, "model_info.json")
    
    if os.path.exists(info_file):
        try:
            with open(info_file, "r") as f:
                model_info = json.load(f)
            
            print("Downloaded Models:")
            print("-" * 80)
            
            downloaded_models = []
            
            for model_type, models in model_info.items():
                print(f"\n{model_type.upper()} MODELS:")
                print("-" * 40)
                
                for model_name, info in models.items():
                    print(f"  {model_name}")
                    print(f"    Downloaded: {info['downloaded']}")
                    print(f"    Last Used: {info.get('last_used', 'Never')}")
                    print(f"    Size: {info.get('size', 'Unknown')}")
                    print(f"    Path: {info.get('path', 'Unknown')}")
                    print()
                    
                    if info['downloaded']:
                        downloaded_models.append((model_type, model_name))
            
            return downloaded_models
        
        except Exception as e:
            print(f"Error reading model info: {e}")
            return []
    
    else:
        print("No downloaded models found.")
        return []

def download_model(model_type, model_name, cache_dir=None, force=False):
    """Download a model."""
    cache_dir = get_cache_dir(cache_dir)
    
    # Check if model exists in MODEL_INFO
    if model_type not in MODEL_INFO or model_name not in MODEL_INFO[model_type]:
        print(f"Error: Model {model_name} of type {model_type} not found in available models.")
        return False
    
    # Get model info
    model_info = MODEL_INFO[model_type][model_name]
    
    # Create model directory
    model_dir = os.path.join(cache_dir, model_type, model_name)
    os.makedirs(model_dir, exist_ok=True)
    
    # Check if model is already downloaded
    info_file = os.path.join(cache_dir, "model_info.json")
    
    if os.path.exists(info_file):
        try:
            with open(info_file, "r") as f:
                info = json.load(f)
            
            if model_type in info and model_name in info[model_type] and info[model_type][model_name]["downloaded"] and not force:
                print(f"Model {model_name} is already downloaded. Use --force to re-download.")
                return True
        
        except Exception:
            # If there's an error reading the file, continue with download
            pass
    
    # Download model based on source
    if model_info["source"] == "huggingface":
        # Use transformers to download the model
        try:
            from transformers import AutoModel, AutoFeatureExtractor
            
            print(f"Downloading {model_name} from Hugging Face...")
            
            # Download model and feature extractor
            model = AutoModel.from_pretrained(model_name)
            feature_extractor = AutoFeatureExtractor.from_pretrained(model_name)
            
            # Save model and feature extractor
            model.save_pretrained(model_dir)
            feature_extractor.save_pretrained(model_dir)
            
            print(f"Model {model_name} downloaded successfully.")
        
        except Exception as e:
            print(f"Error downloading model {model_name}: {e}")
            return False
    
    elif model_info["source"] == "torchvision":
        # Use torchvision to download the model
        try:
            import torchvision.models as models
            
            print(f"Downloading {model_name} from torchvision...")
            
            # Get model function
            if model_name == "deeplabv3_resnet101":
                model_fn = models.segmentation.deeplabv3_resnet101
            elif model_name == "fcn_resnet101":
                model_fn = models.segmentation.fcn_resnet101
            else:
                print(f"Error: Unknown torchvision model {model_name}")
                return False
            
            # Download model
            model = model_fn(pretrained=True)
            
            # Save model
            torch.save(model.state_dict(), os.path.join(model_dir, "model.pth"))
            
            print(f"Model {model_name} downloaded successfully.")
        
        except Exception as e:
            print(f"Error downloading model {model_name}: {e}")
            return False
    
    else:
        print(f"Error: Unknown model source {model_info['source']}")
        return False
    
    # Update model info
    update_model_info(model_type, model_name, {"downloaded": True, "path": model_dir}, cache_dir)
    
    return True

def update_model_info(model_type, model_name, info, cache_dir=None):
    """Update model information."""
    cache_dir = get_cache_dir(cache_dir)
    
    # Get model info file
    info_file = os.path.join(cache_dir, "model_info.json")
    
    # Load existing info or create new
    if os.path.exists(info_file):
        try:
            with open(info_file, "r") as f:
                model_info = json.load(f)
        except Exception:
            model_info = {}
    else:
        model_info = {}
    
    # Update info
    if model_type not in model_info:
        model_info[model_type] = {}
    
    if model_name not in model_info[model_type]:
        model_info[model_type][model_name] = {}
    
    model_info[model_type][model_name].update(info)
    
    # Save info
    with open(info_file, "w") as f:
        json.dump(model_info, f, indent=2)

def delete_model(model_type, model_name, cache_dir=None):
    """Delete a downloaded model."""
    cache_dir = get_cache_dir(cache_dir)
    
    # Get model info file
    info_file = os.path.join(cache_dir, "model_info.json")
    
    if os.path.exists(info_file):
        try:
            with open(info_file, "r") as f:
                model_info = json.load(f)
            
            if model_type in model_info and model_name in model_info[model_type] and model_info[model_type][model_name]["downloaded"]:
                # Get model directory
                model_dir = model_info[model_type][model_name]["path"]
                
                # Delete model directory
                if os.path.exists(model_dir):
                    shutil.rmtree(model_dir)
                
                # Update model info
                model_info[model_type][model_name]["downloaded"] = False
                model_info[model_type][model_name]["path"] = None
                
                # Save info
                with open(info_file, "w") as f:
                    json.dump(model_info, f, indent=2)
                
                print(f"Model {model_name} deleted successfully.")
                return True
            
            else:
                print(f"Model {model_name} of type {model_type} not found in downloaded models.")
                return False
        
        except Exception as e:
            print(f"Error deleting model: {e}")
            return False
    
    else:
        print("No downloaded models found.")
        return False

def test_model(model_type, model_name, cache_dir=None):
    """Test a downloaded model."""
    try:
        # Create model factory
        model_factory = ModelFactory(cache_dir=cache_dir)
        
        # Get model
        model = model_factory.get_model(model_type, model_name=model_name)
        
        # Test model with a dummy input
        if model_type == "depth":
            # Create dummy image
            dummy_image = torch.randn(1, 3, 384, 384)
            
            # Run model
            print(f"Testing depth model {model_name}...")
            _ = model.model(dummy_image)
            
            print(f"Model {model_name} tested successfully.")
            return True
        
        elif model_type == "segmentation":
            # Create dummy image
            dummy_image = torch.randn(1, 3, 384, 384)
            
            # Run model
            print(f"Testing segmentation model {model_name}...")
            _ = model.model(dummy_image)
            
            print(f"Model {model_name} tested successfully.")
            return True
        
        else:
            print(f"Error: Unknown model type {model_type}")
            return False
    
    except Exception as e:
        print(f"Error testing model: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Model manager for AI Text Behind Image")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List available models")
    list_parser.add_argument("--downloaded", action="store_true", help="List only downloaded models")
    list_parser.add_argument("--cache-dir", help="Model cache directory")
    
    # Download command
    download_parser = subparsers.add_parser("download", help="Download a model")
    download_parser.add_argument("--type", required=True, choices=["depth", "segmentation"], help="Model type")
    download_parser.add_argument("--name", required=True, help="Model name")
    download_parser.add_argument("--cache-dir", help="Model cache directory")
    download_parser.add_argument("--force", action="store_true", help="Force re-download")
    
    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a downloaded model")
    delete_parser.add_argument("--type", required=True, choices=["depth", "segmentation"], help="Model type")
    delete_parser.add_argument("--name", required=True, help="Model name")
    delete_parser.add_argument("--cache-dir", help="Model cache directory")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Test a downloaded model")
    test_parser.add_argument("--type", required=True, choices=["depth", "segmentation"], help="Model type")
    test_parser.add_argument("--name", required=True, help="Model name")
    test_parser.add_argument("--cache-dir", help="Model cache directory")
    
    # Download all command
    download_all_parser = subparsers.add_parser("download-all", help="Download all models")
    download_all_parser.add_argument("--cache-dir", help="Model cache directory")
    download_all_parser.add_argument("--force", action="store_true", help="Force re-download")
    
    args = parser.parse_args()
    
    if args.command == "list":
        if args.downloaded:
            list_downloaded_models(args.cache_dir)
        else:
            list_available_models()
    
    elif args.command == "download":
        download_model(args.type, args.name, args.cache_dir, args.force)
    
    elif args.command == "delete":
        delete_model(args.type, args.name, args.cache_dir)
    
    elif args.command == "test":
        test_model(args.type, args.name, args.cache_dir)
    
    elif args.command == "download-all":
        for model_type, models in MODEL_INFO.items():
            for model_name in models:
                download_model(model_type, model_name, args.cache_dir, args.force)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()