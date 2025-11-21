import os
import sys
import argparse
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageFont, ImageDraw
import cv2
import torch

# Import local modules
try:
    from image_utils import (
        pil_to_numpy, numpy_to_pil, 
        visualize_depth_map, create_depth_layers,
        find_optimal_text_region
    )
    from text_renderer import TextRenderer, AdvancedTextRenderer
    from ai_models import ModelFactory
except ImportError:
    print("Error: Required modules not found. Make sure you're in the correct directory.")
    sys.exit(1)

def load_sample_image(image_path):
    """Load a sample image for demonstration."""
    try:
        # Check if the image exists
        if not os.path.exists(image_path):
            print(f"Error: Image not found at {image_path}")
            return None
        
        # Load the image
        image = Image.open(image_path).convert("RGB")
        return image
    
    except Exception as e:
        print(f"Error loading image: {e}")
        return None

def demonstrate_effects(image, text="Sample Text", font_path=None, font_size=60):
    """Demonstrate different text effects."""
    # Load models
    print("Loading AI models...")
    model_factory = ModelFactory()
    depth_model = model_factory.get_model("depth")
    segmentation_model = model_factory.get_model("segmentation")
    
    # Process image
    print("Processing image...")
    image_np = pil_to_numpy(image)
    
    # Get depth map
    depth_map = depth_model.predict(image_np)
    
    # Get segmentation mask
    segmentation_mask = segmentation_model.predict(image_np)
    
    # Create text renderer
    if font_path and os.path.exists(font_path):
        font = ImageFont.truetype(font_path, font_size)
    else:
        # Use default font
        font = ImageFont.truetype("arial.ttf" if os.name == "nt" else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
    
    # Create basic text renderer
    basic_renderer = TextRenderer(font=font)
    
    # Create advanced text renderer
    advanced_renderer = AdvancedTextRenderer(font=font)
    
    # Find optimal text region
    region = find_optimal_text_region(depth_map, min_size=(font_size*len(text)//2, font_size*2))
    text_x, text_y = region["center"]
    
    # Create figure for visualization
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
    
    # Segmentation mask
    axs[0, 2].imshow(segmentation_mask)
    axs[0, 2].set_title("Segmentation Mask")
    axs[0, 2].axis("off")
    
    # Basic text rendering
    basic_image = image.copy()
    basic_renderer.render_text(basic_image, text, (text_x, text_y), color=(255, 255, 255))
    axs[1, 0].imshow(basic_image)
    axs[1, 0].set_title("Basic Text")
    axs[1, 0].axis("off")
    
    # Text with shadow
    shadow_image = image.copy()
    basic_renderer.render_text(shadow_image, text, (text_x, text_y), color=(255, 255, 255), shadow=True, shadow_color=(0, 0, 0))
    axs[1, 1].imshow(shadow_image)
    axs[1, 1].set_title("Text with Shadow")
    axs[1, 1].axis("off")
    
    # Text with glow
    glow_image = image.copy()
    basic_renderer.render_text(glow_image, text, (text_x, text_y), color=(255, 255, 255), glow=True, glow_color=(0, 0, 255))
    axs[1, 2].imshow(glow_image)
    axs[1, 2].set_title("Text with Glow")
    axs[1, 2].axis("off")
    
    # Text with perspective
    perspective_image = image.copy()
    advanced_renderer.render_text_with_depth(perspective_image, text, (text_x, text_y), depth_map, color=(255, 255, 255), perspective_strength=0.5)
    axs[2, 0].imshow(perspective_image)
    axs[2, 0].set_title("Text with Perspective")
    axs[2, 0].axis("off")
    
    # Text with lighting adaptation
    lighting_image = image.copy()
    advanced_renderer.render_text_with_depth(lighting_image, text, (text_x, text_y), depth_map, color=(255, 255, 255), adapt_lighting=True)
    axs[2, 1].imshow(lighting_image)
    axs[2, 1].set_title("Text with Lighting Adaptation")
    axs[2, 1].axis("off")
    
    # Full effect
    full_effect_image = image.copy()
    advanced_renderer.render_text_with_depth(
        full_effect_image, text, (text_x, text_y), depth_map, 
        color=(255, 255, 255), 
        perspective_strength=0.5,
        shadow=True,
        shadow_strength=0.7,
        adapt_lighting=True,
        glow=True,
        glow_color=(0, 100, 255)
    )
    axs[2, 2].imshow(full_effect_image)
    axs[2, 2].set_title("Full Effect")
    axs[2, 2].axis("off")
    
    # Adjust layout
    plt.tight_layout()
    
    return fig, full_effect_image

def main():
    parser = argparse.ArgumentParser(description="Demonstrate text effects")
    
    parser.add_argument("--image", required=True, help="Path to the input image")
    parser.add_argument("--text", default="Sample Text", help="Text to render")
    parser.add_argument("--font", help="Path to a font file")
    parser.add_argument("--size", type=int, default=60, help="Font size")
    parser.add_argument("--output", default="effects_demo.png", help="Output image path")
    
    args = parser.parse_args()
    
    # Load image
    image = load_sample_image(args.image)
    if image is None:
        return 1
    
    # Demonstrate effects
    fig, result_image = demonstrate_effects(image, args.text, args.font, args.size)
    
    # Save figure
    fig.savefig(args.output, dpi=100, bbox_inches="tight")
    print(f"Effects demonstration saved to {args.output}")
    
    # Save result image
    result_path = os.path.splitext(args.output)[0] + "_result.png"
    result_image.save(result_path)
    print(f"Result image saved to {result_path}")
    
    # Show figure
    plt.show()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())