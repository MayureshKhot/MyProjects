import os
import sys
import argparse
import numpy as np
from PIL import Image, ImageFont
import matplotlib.pyplot as plt

# Import local modules
try:
    from ai_models import ModelFactory
    from text_renderer import AdvancedTextRenderer
    from image_utils import pil_to_numpy, numpy_to_pil, visualize_depth_map, find_optimal_text_region
except ImportError:
    print("Error: Required modules not found. Make sure you're in the correct directory.")
    sys.exit(1)

def example_basic_text_insertion(image_path, text="Hello World", output_path="example_basic.png"):
    """Demonstrate basic text insertion."""
    print(f"Running basic text insertion example with '{text}'...")
    
    # Load image
    try:
        image = Image.open(image_path).convert("RGB")
    except Exception as e:
        print(f"Error loading image: {e}")
        return False
    
    # Load models
    model_factory = ModelFactory()
    depth_model = model_factory.get_model("depth")
    
    # Get depth map
    image_np = pil_to_numpy(image)
    depth_map = depth_model.predict(image_np)
    
    # Find optimal text region
    region = find_optimal_text_region(depth_map)
    text_position = region["center"]
    
    # Create text renderer
    font = ImageFont.truetype("arial.ttf" if os.name == "nt" else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 60)
    renderer = AdvancedTextRenderer(font=font)
    
    # Render text
    result_image = image.copy()
    renderer.render_text_with_depth(
        result_image, text, text_position, depth_map,
        color=(255, 255, 255),
        shadow=True
    )
    
    # Save result
    result_image.save(output_path)
    print(f"Result saved to {output_path}")
    
    return True

def example_advanced_text_insertion(image_path, text="Hello World", output_path="example_advanced.png"):
    """Demonstrate advanced text insertion with multiple effects."""
    print(f"Running advanced text insertion example with '{text}'...")
    
    # Load image
    try:
        image = Image.open(image_path).convert("RGB")
    except Exception as e:
        print(f"Error loading image: {e}")
        return False
    
    # Load models
    model_factory = ModelFactory()
    depth_model = model_factory.get_model("depth")
    segmentation_model = model_factory.get_model("segmentation")
    
    # Get depth map and segmentation mask
    image_np = pil_to_numpy(image)
    depth_map = depth_model.predict(image_np)
    segmentation_mask = segmentation_model.predict(image_np)
    
    # Find optimal text region
    region = find_optimal_text_region(depth_map)
    text_position = region["center"]
    
    # Create text renderer
    font = ImageFont.truetype("arial.ttf" if os.name == "nt" else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 60)
    renderer = AdvancedTextRenderer(font=font)
    
    # Render text with advanced effects
    result_image = image.copy()
    renderer.render_text_with_depth(
        result_image, text, text_position, depth_map,
        color=(255, 255, 255),
        perspective_strength=0.5,
        shadow=True,
        shadow_strength=0.7,
        adapt_lighting=True,
        glow=True,
        glow_color=(0, 100, 255)
    )
    
    # Save result
    result_image.save(output_path)
    print(f"Result saved to {output_path}")
    
    # Create visualization
    fig, axs = plt.subplots(2, 2, figsize=(12, 10))
    
    # Original image
    axs[0, 0].imshow(image)
    axs[0, 0].set_title("Original Image")
    axs[0, 0].axis("off")
    
    # Depth map
    depth_vis = visualize_depth_map(depth_map)
    axs[0, 1].imshow(depth_vis)
    axs[0, 1].set_title("Depth Map")
    axs[0, 1].axis("off")
    
    # Segmentation mask
    axs[1, 0].imshow(segmentation_mask)
    axs[1, 0].set_title("Segmentation Mask")
    axs[1, 0].axis("off")
    
    # Result
    axs[1, 1].imshow(result_image)
    axs[1, 1].set_title("Result with Text")
    axs[1, 1].axis("off")
    
    # Save visualization
    vis_path = os.path.splitext(output_path)[0] + "_visualization.png"
    plt.tight_layout()
    plt.savefig(vis_path)
    print(f"Visualization saved to {vis_path}")
    
    return True

def example_effect_comparison(image_path, text="Hello World", output_path="example_effects.png"):
    """Demonstrate different text effects for comparison."""
    print(f"Running effect comparison example with '{text}'...")
    
    # Load image
    try:
        image = Image.open(image_path).convert("RGB")
    except Exception as e:
        print(f"Error loading image: {e}")
        return False
    
    # Load models
    model_factory = ModelFactory()
    depth_model = model_factory.get_model("depth")
    
    # Get depth map
    image_np = pil_to_numpy(image)
    depth_map = depth_model.predict(image_np)
    
    # Find optimal text region
    region = find_optimal_text_region(depth_map)
    text_position = region["center"]
    
    # Create text renderer
    font = ImageFont.truetype("arial.ttf" if os.name == "nt" else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 60)
    renderer = AdvancedTextRenderer(font=font)
    
    # Create figure for comparison
    fig, axs = plt.subplots(3, 3, figsize=(15, 15))
    
    # Original image
    axs[0, 0].imshow(image)
    axs[0, 0].set_title("Original Image")
    axs[0, 0].axis("off")
    
    # Depth map
    depth_vis = visualize_depth_map(depth_map)
    axs[0, 1].imshow(depth_vis)
    axs[0, 1].set_title("Depth Map")
    axs[0, 1].axis("off")
    
    # Basic text
    basic_image = image.copy()
    renderer.render_text(basic_image, text, text_position, color=(255, 255, 255))
    axs[0, 2].imshow(basic_image)
    axs[0, 2].set_title("Basic Text")
    axs[0, 2].axis("off")
    
    # Text with shadow
    shadow_image = image.copy()
    renderer.render_text(shadow_image, text, text_position, color=(255, 255, 255), shadow=True)
    axs[1, 0].imshow(shadow_image)
    axs[1, 0].set_title("Text with Shadow")
    axs[1, 0].axis("off")
    
    # Text with glow
    glow_image = image.copy()
    renderer.render_text(glow_image, text, text_position, color=(255, 255, 255), glow=True)
    axs[1, 1].imshow(glow_image)
    axs[1, 1].set_title("Text with Glow")
    axs[1, 1].axis("off")
    
    # Text with perspective
    perspective_image = image.copy()
    renderer.render_text_with_depth(perspective_image, text, text_position, depth_map, color=(255, 255, 255), perspective_strength=0.5)
    axs[1, 2].imshow(perspective_image)
    axs[1, 2].set_title("Text with Perspective")
    axs[1, 2].axis("off")
    
    # Text with lighting adaptation
    lighting_image = image.copy()
    renderer.render_text_with_depth(lighting_image, text, text_position, depth_map, color=(255, 255, 255), adapt_lighting=True)
    axs[2, 0].imshow(lighting_image)
    axs[2, 0].set_title("Text with Lighting Adaptation")
    axs[2, 0].axis("off")
    
    # Text with perspective and shadow
    ps_image = image.copy()
    renderer.render_text_with_depth(ps_image, text, text_position, depth_map, color=(255, 255, 255), perspective_strength=0.5, shadow=True)
    axs[2, 1].imshow(ps_image)
    axs[2, 1].set_title("Perspective + Shadow")
    axs[2, 1].axis("off")
    
    # Full effect
    full_image = image.copy()
    renderer.render_text_with_depth(
        full_image, text, text_position, depth_map,
        color=(255, 255, 255),
        perspective_strength=0.5,
        shadow=True,
        shadow_strength=0.7,
        adapt_lighting=True,
        glow=True,
        glow_color=(0, 100, 255)
    )
    axs[2, 2].imshow(full_image)
    axs[2, 2].set_title("Full Effect")
    axs[2, 2].axis("off")
    
    # Save comparison
    plt.tight_layout()
    plt.savefig(output_path)
    print(f"Effect comparison saved to {output_path}")
    
    # Save full effect image
    full_path = os.path.splitext(output_path)[0] + "_full.png"
    full_image.save(full_path)
    print(f"Full effect image saved to {full_path}")
    
    return True

def main():
    parser = argparse.ArgumentParser(description="Example scripts for AI Text Behind Image")
    
    parser.add_argument("--image", required=True, help="Path to the input image")
    parser.add_argument("--text", default="Hello World", help="Text to insert")
    parser.add_argument("--output-dir", default="examples", help="Output directory")
    parser.add_argument("--example", choices=["basic", "advanced", "effects", "all"], default="all", help="Example to run")
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Run examples
    if args.example == "basic" or args.example == "all":
        output_path = os.path.join(args.output_dir, "example_basic.png")
        example_basic_text_insertion(args.image, args.text, output_path)
    
    if args.example == "advanced" or args.example == "all":
        output_path = os.path.join(args.output_dir, "example_advanced.png")
        example_advanced_text_insertion(args.image, args.text, output_path)
    
    if args.example == "effects" or args.example == "all":
        output_path = os.path.join(args.output_dir, "example_effects.png")
        example_effect_comparison(args.image, args.text, output_path)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())