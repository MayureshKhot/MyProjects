import os
import sys
import time
import argparse
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import torch

# Import local modules
try:
    from ai_models import ModelFactory
    from image_utils import pil_to_numpy, numpy_to_pil, visualize_depth_map
except ImportError:
    print("Error: Required modules not found. Make sure you're in the correct directory.")
    sys.exit(1)

def benchmark_depth_models(image_paths, models=None, iterations=3):
    """Benchmark different depth estimation models."""
    # Available depth models
    if models is None:
        models = ["Intel/dpt-large", "Intel/dpt-hybrid-midas"]
    
    # Results dictionary
    results = {}
    
    # Create model factory
    model_factory = ModelFactory()
    
    # Process each image
    for image_path in image_paths:
        print(f"Processing {image_path}...")
        
        # Load image
        try:
            image = Image.open(image_path).convert("RGB")
            image_np = pil_to_numpy(image)
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
            continue
        
        # Process with each model
        for model_name in models:
            print(f"  Testing model: {model_name}")
            
            # Initialize model
            try:
                model = model_factory.get_model("depth", model_name=model_name)
            except Exception as e:
                print(f"  Error initializing model {model_name}: {e}")
                continue
            
            # Warm-up run
            _ = model.predict(image_np)
            
            # Benchmark runs
            times = []
            for i in range(iterations):
                start_time = time.time()
                depth_map = model.predict(image_np)
                end_time = time.time()
                elapsed = end_time - start_time
                times.append(elapsed)
                print(f"    Run {i+1}/{iterations}: {elapsed:.4f} seconds")
            
            # Calculate statistics
            avg_time = np.mean(times)
            std_time = np.std(times)
            
            # Store results
            if model_name not in results:
                results[model_name] = []
            
            results[model_name].append({
                "image": os.path.basename(image_path),
                "times": times,
                "avg_time": avg_time,
                "std_time": std_time,
                "depth_map": depth_map
            })
    
    return results

def benchmark_segmentation_models(image_paths, models=None, iterations=3):
    """Benchmark different segmentation models."""
    # Available segmentation models
    if models is None:
        models = ["deeplabv3_resnet101", "fcn_resnet101"]
    
    # Results dictionary
    results = {}
    
    # Create model factory
    model_factory = ModelFactory()
    
    # Process each image
    for image_path in image_paths:
        print(f"Processing {image_path}...")
        
        # Load image
        try:
            image = Image.open(image_path).convert("RGB")
            image_np = pil_to_numpy(image)
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
            continue
        
        # Process with each model
        for model_name in models:
            print(f"  Testing model: {model_name}")
            
            # Initialize model
            try:
                model = model_factory.get_model("segmentation", model_name=model_name)
            except Exception as e:
                print(f"  Error initializing model {model_name}: {e}")
                continue
            
            # Warm-up run
            _ = model.predict(image_np)
            
            # Benchmark runs
            times = []
            for i in range(iterations):
                start_time = time.time()
                segmentation_mask = model.predict(image_np)
                end_time = time.time()
                elapsed = end_time - start_time
                times.append(elapsed)
                print(f"    Run {i+1}/{iterations}: {elapsed:.4f} seconds")
            
            # Calculate statistics
            avg_time = np.mean(times)
            std_time = np.std(times)
            
            # Store results
            if model_name not in results:
                results[model_name] = []
            
            results[model_name].append({
                "image": os.path.basename(image_path),
                "times": times,
                "avg_time": avg_time,
                "std_time": std_time,
                "segmentation_mask": segmentation_mask
            })
    
    return results

def visualize_benchmark_results(depth_results, segmentation_results, output_path="benchmark_results.png"):
    """Visualize benchmark results."""
    # Create figure
    fig = plt.figure(figsize=(15, 10))
    
    # Add depth model results
    if depth_results:
        ax1 = fig.add_subplot(2, 1, 1)
        
        # Extract model names and average times
        model_names = list(depth_results.keys())
        avg_times = [np.mean([r["avg_time"] for r in depth_results[model]]) for model in model_names]
        std_times = [np.mean([r["std_time"] for r in depth_results[model]]) for model in model_names]
        
        # Create bar chart
        bars = ax1.bar(model_names, avg_times, yerr=std_times, capsize=10)
        
        # Add labels and title
        ax1.set_ylabel("Average Time (seconds)")
        ax1.set_title("Depth Estimation Model Performance")
        
        # Add text labels
        for bar, time in zip(bars, avg_times):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                    f"{time:.4f}s", ha="center", va="bottom")
    
    # Add segmentation model results
    if segmentation_results:
        ax2 = fig.add_subplot(2, 1, 2)
        
        # Extract model names and average times
        model_names = list(segmentation_results.keys())
        avg_times = [np.mean([r["avg_time"] for r in segmentation_results[model]]) for model in model_names]
        std_times = [np.mean([r["std_time"] for r in segmentation_results[model]]) for model in model_names]
        
        # Create bar chart
        bars = ax2.bar(model_names, avg_times, yerr=std_times, capsize=10)
        
        # Add labels and title
        ax2.set_ylabel("Average Time (seconds)")
        ax2.set_title("Segmentation Model Performance")
        
        # Add text labels
        for bar, time in zip(bars, avg_times):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                    f"{time:.4f}s", ha="center", va="bottom")
    
    # Adjust layout and save
    plt.tight_layout()
    plt.savefig(output_path)
    print(f"Benchmark results saved to {output_path}")
    
    return fig

def visualize_model_outputs(depth_results, segmentation_results, output_dir="benchmark_outputs"):
    """Visualize model outputs for comparison."""
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Process depth model outputs
    if depth_results:
        for model_name, results in depth_results.items():
            for result in results:
                # Create figure
                fig, ax = plt.subplots(1, 1, figsize=(10, 8))
                
                # Visualize depth map
                depth_vis = visualize_depth_map(result["depth_map"])
                ax.imshow(depth_vis)
                
                # Add title
                ax.set_title(f"Depth Map: {model_name} - {result['image']}\nTime: {result['avg_time']:.4f}s")
                ax.axis("off")
                
                # Save figure
                output_path = os.path.join(output_dir, f"depth_{model_name}_{result['image']}.png")
                plt.savefig(output_path)
                plt.close(fig)
    
    # Process segmentation model outputs
    if segmentation_results:
        for model_name, results in segmentation_results.items():
            for result in results:
                # Create figure
                fig, ax = plt.subplots(1, 1, figsize=(10, 8))
                
                # Visualize segmentation mask
                ax.imshow(result["segmentation_mask"])
                
                # Add title
                ax.set_title(f"Segmentation: {model_name} - {result['image']}\nTime: {result['avg_time']:.4f}s")
                ax.axis("off")
                
                # Save figure
                output_path = os.path.join(output_dir, f"segmentation_{model_name}_{result['image']}.png")
                plt.savefig(output_path)
                plt.close(fig)
    
    print(f"Model outputs saved to {output_dir}")

def main():
    parser = argparse.ArgumentParser(description="Benchmark AI models for AI Text Behind Image")
    
    parser.add_argument("--images", nargs="+", required=True, help="Paths to input images")
    parser.add_argument("--depth-models", nargs="*", help="Depth estimation models to benchmark")
    parser.add_argument("--segmentation-models", nargs="*", help="Segmentation models to benchmark")
    parser.add_argument("--iterations", type=int, default=3, help="Number of iterations for each benchmark")
    parser.add_argument("--output", default="benchmark_results.png", help="Output path for benchmark results")
    parser.add_argument("--output-dir", default="benchmark_outputs", help="Output directory for model outputs")
    
    args = parser.parse_args()
    
    # Check if CUDA is available
    cuda_available = torch.cuda.is_available()
    device = "cuda" if cuda_available else "cpu"
    print(f"Using device: {device}")
    
    # Benchmark depth models
    depth_results = benchmark_depth_models(args.images, args.depth_models, args.iterations)
    
    # Benchmark segmentation models
    segmentation_results = benchmark_segmentation_models(args.images, args.segmentation_models, args.iterations)
    
    # Visualize benchmark results
    visualize_benchmark_results(depth_results, segmentation_results, args.output)
    
    # Visualize model outputs
    visualize_model_outputs(depth_results, segmentation_results, args.output_dir)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())