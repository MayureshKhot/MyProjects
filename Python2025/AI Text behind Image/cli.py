import os
import sys
import argparse
from PIL import Image
import numpy as np

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our modules
from ai_models import ModelFactory
from text_renderer import AdvancedTextRenderer
from image_utils import visualize_depth_map

def process_single_image(image_path, output_path, text, font_name, font_size, color, 
                        opacity, perspective, shadow_strength, depth_threshold,
                        show_depth_map=False):
    """Process a single image with text."""
    try:
        # Check if input file exists
        if not os.path.isfile(image_path):
            print(f"Error: Input file '{image_path}' does not exist.")
            return False
        
        # Load image
        print(f"Loading image: {image_path}")
        image = Image.open(image_path)
        
        # Load models
        print("Loading AI models...")
        depth_model = ModelFactory.get_depth_model()
        segmentation_model = ModelFactory.get_segmentation_model()
        
        # Get depth map
        print("Analyzing image depth...")
        depth_map = depth_model.predict(image)
        
        # Get segmentation mask
        print("Segmenting image...")
        segmentation_mask = segmentation_model.predict(image)
        
        # Create text renderer
        renderer = AdvancedTextRenderer()
        
        # Set up effects
        effects = {
            'perspective': perspective,
            'shadow': True,
            'shadow_strength': shadow_strength,
            'lighting_adaptation': True,
            'depth_threshold': depth_threshold
        }
        
        # Render text with depth awareness
        print(f"Rendering text: '{text}'")
        result_image = renderer.render_text_with_depth(
            image, text, depth_map, 
            font_name=font_name, font_size=font_size,
            color=color, opacity=opacity, effects=effects
        )
        
        # Save result
        print(f"Saving result to: {output_path}")
        result_image.save(output_path)
        
        # Save depth map if requested
        if show_depth_map:
            depth_vis = visualize_depth_map(depth_map)
            depth_vis_pil = Image.fromarray(depth_vis)
            
            # Create depth map filename
            base_name, ext = os.path.splitext(output_path)
            depth_path = f"{base_name}_depth{ext}"
            
            print(f"Saving depth map to: {depth_path}")
            depth_vis_pil.save(depth_path)
        
        print("Processing complete!")
        return True
    
    except Exception as e:
        print(f"Error processing image: {e}")
        return False

def parse_color(color_str):
    """Parse color string in hex format (#RRGGBB) to RGB tuple."""
    color_str = color_str.lstrip('#')
    return tuple(int(color_str[i:i+2], 16) for i in (0, 2, 4))

def main():
    parser = argparse.ArgumentParser(description="AI Text Behind Image - Command Line Interface")
    
    parser.add_argument("input_path", help="Path to input image")
    parser.add_argument("output_path", help="Path to save output image")
    parser.add_argument("text", help="Text to insert into image")
    
    parser.add_argument("--font", default="arial.ttf", help="Font file name")
    parser.add_argument("--size", type=int, default=40, help="Font size")
    parser.add_argument("--color", default="#FFFFFF", help="Text color in hex format (#RRGGBB)")
    parser.add_argument("--opacity", type=float, default=0.9, help="Text opacity (0.0-1.0)")
    parser.add_argument("--perspective", type=float, default=0.2, help="Perspective effect strength (0.0-1.0)")
    parser.add_argument("--shadow", type=float, default=0.5, help="Shadow strength (0.0-1.0)")
    parser.add_argument("--depth", type=float, default=0.5, help="Depth threshold (0.0-1.0)")
    parser.add_argument("--show-depth", action="store_true", help="Save depth map visualization")
    
    args = parser.parse_args()
    
    # Parse color
    color = parse_color(args.color)
    
    # Process image
    process_single_image(
        args.input_path, args.output_path, args.text,
        font_name=args.font, font_size=args.size,
        color=color, opacity=args.opacity,
        perspective=args.perspective, shadow_strength=args.shadow,
        depth_threshold=args.depth, show_depth_map=args.show_depth
    )

if __name__ == "__main__":
    main()