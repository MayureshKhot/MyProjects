import os
import sys
import argparse
from PIL import Image
import glob
from tqdm import tqdm
import time

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our modules
from ai_models import ModelFactory
from text_renderer import AdvancedTextRenderer

def process_image(image_path, output_dir, text, font_name, font_size, color, 
                 opacity, perspective, shadow_strength, depth_threshold):
    """Process a single image with text."""
    try:
        # Load image
        image = Image.open(image_path)
        
        # Load models if not already loaded
        global depth_model, segmentation_model
        if 'depth_model' not in globals():
            depth_model = ModelFactory.get_depth_model()
        if 'segmentation_model' not in globals():
            segmentation_model = ModelFactory.get_segmentation_model()
        
        # Get depth map
        depth_map = depth_model.predict(image)
        
        # Get segmentation mask
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
        result_image = renderer.render_text_with_depth(
            image, text, depth_map, 
            font_name=font_name, font_size=font_size,
            color=color, opacity=opacity, effects=effects
        )
        
        # Create output filename
        base_name = os.path.basename(image_path)
        name, ext = os.path.splitext(base_name)
        output_path = os.path.join(output_dir, f"{name}_text{ext}")
        
        # Save result
        result_image.save(output_path)
        
        return True, output_path
    
    except Exception as e:
        return False, str(e)

def batch_process(input_dir, output_dir, text, font_name="arial.ttf", font_size=40, 
                 color=(255, 255, 255), opacity=0.9, perspective=0.2, 
                 shadow_strength=0.5, depth_threshold=0.5, extensions=None):
    """Process all images in a directory."""
    # Default extensions if none provided
    if extensions is None:
        extensions = ["jpg", "jpeg", "png", "webp"]
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all image files
    image_files = []
    for ext in extensions:
        pattern = os.path.join(input_dir, f"*.{ext}")
        image_files.extend(glob.glob(pattern))
        pattern = os.path.join(input_dir, f"*.{ext.upper()}")
        image_files.extend(glob.glob(pattern))
    
    if not image_files:
        print(f"No images found in {input_dir} with extensions {extensions}")
        return
    
    print(f"Found {len(image_files)} images to process")
    
    # Process each image
    results = []
    for image_path in tqdm(image_files, desc="Processing images"):
        success, result = process_image(
            image_path, output_dir, text, font_name, font_size,
            color, opacity, perspective, shadow_strength, depth_threshold
        )
        
        results.append((image_path, success, result))
        
        # Small delay to prevent GPU memory issues
        time.sleep(0.1)
    
    # Print summary
    print("\nProcessing complete!")
    print(f"Successfully processed: {sum(1 for _, success, _ in results if success)}/{len(results)}")
    
    # Print failures if any
    failures = [(path, error) for path, success, error in results if not success]
    if failures:
        print("\nFailed images:")
        for path, error in failures:
            print(f"  {os.path.basename(path)}: {error}")
    
    print(f"\nResults saved to: {output_dir}")

def parse_color(color_str):
    """Parse color string in hex format (#RRGGBB) to RGB tuple."""
    color_str = color_str.lstrip('#')
    return tuple(int(color_str[i:i+2], 16) for i in (0, 2, 4))

def main():
    parser = argparse.ArgumentParser(description="Batch process images with AI text insertion")
    
    parser.add_argument("input_dir", help="Directory containing input images")
    parser.add_argument("output_dir", help="Directory to save processed images")
    parser.add_argument("text", help="Text to insert into images")
    
    parser.add_argument("--font", default="arial.ttf", help="Font file name")
    parser.add_argument("--size", type=int, default=40, help="Font size")
    parser.add_argument("--color", default="#FFFFFF", help="Text color in hex format (#RRGGBB)")
    parser.add_argument("--opacity", type=float, default=0.9, help="Text opacity (0.0-1.0)")
    parser.add_argument("--perspective", type=float, default=0.2, help="Perspective effect strength (0.0-1.0)")
    parser.add_argument("--shadow", type=float, default=0.5, help="Shadow strength (0.0-1.0)")
    parser.add_argument("--depth", type=float, default=0.5, help="Depth threshold (0.0-1.0)")
    parser.add_argument("--extensions", nargs="+", default=["jpg", "jpeg", "png", "webp"], 
                        help="Image file extensions to process")
    
    args = parser.parse_args()
    
    # Parse color
    color = parse_color(args.color)
    
    # Run batch processing
    batch_process(
        args.input_dir, args.output_dir, args.text,
        font_name=args.font, font_size=args.size,
        color=color, opacity=args.opacity,
        perspective=args.perspective, shadow_strength=args.shadow,
        depth_threshold=args.depth, extensions=args.extensions
    )

if __name__ == "__main__":
    main()