import os
import sys
import platform
import glob
import argparse
from PIL import ImageFont, Image, ImageDraw
import matplotlib.pyplot as plt
import numpy as np

def find_system_fonts():
    """Find available system fonts."""
    system = platform.system()
    font_paths = []
    
    if system == "Windows":
        # Windows font directories
        font_dirs = [
            os.path.join(os.environ['WINDIR'], 'Fonts'),
            os.path.join(os.environ['LOCALAPPDATA'], 'Microsoft', 'Windows', 'Fonts')
        ]
        
        # Font extensions
        extensions = ['*.ttf', '*.ttc', '*.otf']
        
        # Find all font files
        for font_dir in font_dirs:
            if os.path.exists(font_dir):
                for ext in extensions:
                    font_paths.extend(glob.glob(os.path.join(font_dir, ext)))
    
    elif system == "Darwin":  # macOS
        # macOS font directories
        font_dirs = [
            '/Library/Fonts',
            '/System/Library/Fonts',
            os.path.expanduser('~/Library/Fonts')
        ]
        
        # Font extensions
        extensions = ['*.ttf', '*.ttc', '*.otf']
        
        # Find all font files
        for font_dir in font_dirs:
            if os.path.exists(font_dir):
                for ext in extensions:
                    font_paths.extend(glob.glob(os.path.join(font_dir, ext)))
    
    elif system == "Linux":
        # Linux font directories
        font_dirs = [
            '/usr/share/fonts',
            '/usr/local/share/fonts',
            os.path.expanduser('~/.fonts')
        ]
        
        # Font extensions
        extensions = ['*.ttf', '*.ttc', '*.otf']
        
        # Find all font files
        for font_dir in font_dirs:
            if os.path.exists(font_dir):
                for ext in extensions:
                    # Recursively search for fonts
                    for root, dirs, files in os.walk(font_dir):
                        font_paths.extend(glob.glob(os.path.join(root, ext)))
    
    return font_paths

def get_font_name(font_path):
    """Try to get the font name from a font file."""
    try:
        # Try to load the font
        font = ImageFont.truetype(font_path, 12)
        
        # Get the font name if available
        if hasattr(font, 'getname'):
            return font.getname()[0]
        
        # Fall back to filename
        return os.path.basename(font_path)
    
    except Exception:
        # If we can't load the font, just return the filename
        return os.path.basename(font_path)

def create_font_preview(font_path, text="Hello World", size=40):
    """Create a preview image for a font."""
    try:
        # Load the font
        font = ImageFont.truetype(font_path, size)
        
        # Create an image
        img_width = 600
        img_height = 100
        image = Image.new('RGB', (img_width, img_height), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # Get text size
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        # Center the text
        x = (img_width - text_width) // 2
        y = (img_height - text_height) // 2
        
        # Draw the text
        draw.text((x, y), text, font=font, fill=(0, 0, 0))
        
        return image
    
    except Exception as e:
        print(f"Error creating preview for {font_path}: {e}")
        return None

def create_font_catalog(output_path="font_catalog.png", num_fonts=20, text="Hello World"):
    """Create a catalog of available fonts."""
    # Find system fonts
    font_paths = find_system_fonts()
    
    if not font_paths:
        print("No fonts found on the system.")
        return
    
    print(f"Found {len(font_paths)} fonts on the system.")
    
    # Limit to requested number of fonts
    if num_fonts < len(font_paths):
        # Take a sample of fonts
        indices = np.linspace(0, len(font_paths) - 1, num_fonts, dtype=int)
        font_paths = [font_paths[i] for i in indices]
    
    # Create figure for the catalog
    fig, axs = plt.subplots(len(font_paths), 1, figsize=(10, len(font_paths) * 1.2))
    
    # If only one font, axs is not an array
    if len(font_paths) == 1:
        axs = [axs]
    
    # Create preview for each font
    for i, font_path in enumerate(font_paths):
        # Get font name
        font_name = get_font_name(font_path)
        
        # Create preview
        preview = create_font_preview(font_path, text)
        
        if preview:
            # Display preview
            axs[i].imshow(preview)
            axs[i].set_title(f"{font_name}")
            axs[i].axis('off')
        else:
            # Display error message
            axs[i].text(0.5, 0.5, f"Error loading {font_name}", 
                       horizontalalignment='center', verticalalignment='center')
            axs[i].axis('off')
    
    # Adjust layout and save
    plt.tight_layout()
    plt.savefig(output_path, dpi=100, bbox_inches='tight')
    print(f"Font catalog saved to {output_path}")
    
    # Return the list of font paths
    return font_paths

def create_font_list(output_path="available_fonts.txt"):
    """Create a list of available fonts."""
    # Find system fonts
    font_paths = find_system_fonts()
    
    if not font_paths:
        print("No fonts found on the system.")
        return
    
    print(f"Found {len(font_paths)} fonts on the system.")
    
    # Create the output file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("Available Fonts\n")
        f.write("-" * 50 + "\n\n")
        
        for i, font_path in enumerate(font_paths):
            # Get font name
            font_name = get_font_name(font_path)
            
            # Write to file
            f.write(f"{i+1}. {font_name}\n")
            f.write(f"   Path: {font_path}\n\n")
    
    print(f"Font list saved to {output_path}")
    return font_paths

def main():
    parser = argparse.ArgumentParser(description="Font utilities for AI Text Behind Image")
    
    parser.add_argument("--catalog", action="store_true", help="Create a font catalog")
    parser.add_argument("--list", action="store_true", help="Create a list of available fonts")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--num-fonts", type=int, default=20, help="Number of fonts to include in catalog")
    parser.add_argument("--text", default="Hello World", help="Text to use in font previews")
    
    args = parser.parse_args()
    
    if args.catalog:
        output_path = args.output or "font_catalog.png"
        create_font_catalog(output_path, args.num_fonts, args.text)
    
    elif args.list:
        output_path = args.output or "available_fonts.txt"
        create_font_list(output_path)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()