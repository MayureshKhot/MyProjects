import os
import sys
import argparse
import json
from PIL import Image
import numpy as np
import cv2

def export_image(image, output_path, format="PNG", quality=95, dpi=(300, 300)):
    """Export an image to a file with the specified format and quality."""
    # Ensure image is a PIL Image
    if not isinstance(image, Image.Image):
        if isinstance(image, np.ndarray):
            # Convert numpy array to PIL Image
            image = Image.fromarray(
                cv2.cvtColor(image, cv2.COLOR_BGR2RGB) if image.shape[2] == 3 else image
            )
        else:
            raise TypeError("Image must be a PIL Image or numpy array")
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    # Determine format from output path if not specified
    if format == "auto":
        format = os.path.splitext(output_path)[1][1:].upper()
        if not format:
            format = "PNG"
    
    # Set save parameters based on format
    save_args = {}
    
    if format.upper() == "JPEG" or format.upper() == "JPG":
        format = "JPEG"
        save_args["quality"] = quality
        save_args["optimize"] = True
    
    elif format.upper() == "PNG":
        save_args["optimize"] = True
    
    elif format.upper() == "WEBP":
        save_args["quality"] = quality
        save_args["method"] = 6  # Highest compression method
    
    elif format.upper() == "TIFF" or format.upper() == "TIF":
        format = "TIFF"
        save_args["compression"] = "tiff_lzw"
    
    # Set DPI
    if dpi:
        save_args["dpi"] = dpi
    
    # Save the image
    image.save(output_path, format=format, **save_args)
    
    return output_path

def export_with_metadata(image, output_path, metadata=None, format="PNG", quality=95, dpi=(300, 300)):
    """Export an image with metadata."""
    # Export the image
    export_image(image, output_path, format, quality, dpi)
    
    # If metadata is provided, save it as a JSON file
    if metadata:
        # Create metadata filename
        metadata_path = os.path.splitext(output_path)[0] + ".json"
        
        # Save metadata
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
    
    return output_path

def export_depth_map(depth_map, output_path, format="PNG", colormap=cv2.COLORMAP_INFERNO):
    """Export a depth map as a colorized image."""
    # Normalize depth map to 0-255
    depth_norm = cv2.normalize(depth_map, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    
    # Apply colormap
    depth_color = cv2.applyColorMap(depth_norm, colormap)
    
    # Convert to PIL Image
    depth_image = Image.fromarray(cv2.cvtColor(depth_color, cv2.COLOR_BGR2RGB))
    
    # Export the image
    export_image(depth_image, output_path, format)
    
    return output_path

def export_segmentation_mask(segmentation_mask, output_path, format="PNG"):
    """Export a segmentation mask as an image."""
    # Ensure mask is a numpy array
    if not isinstance(segmentation_mask, np.ndarray):
        segmentation_mask = np.array(segmentation_mask)
    
    # If mask is grayscale, convert to RGB
    if len(segmentation_mask.shape) == 2 or segmentation_mask.shape[2] == 1:
        # Normalize to 0-255
        mask_norm = cv2.normalize(segmentation_mask, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        
        # Apply colormap
        mask_color = cv2.applyColorMap(mask_norm, cv2.COLORMAP_JET)
        mask_image = Image.fromarray(cv2.cvtColor(mask_color, cv2.COLOR_BGR2RGB))
    else:
        # Already RGB
        mask_image = Image.fromarray(segmentation_mask)
    
    # Export the image
    export_image(mask_image, output_path, format)
    
    return output_path

def export_project(image, depth_map, segmentation_mask, output_dir, base_name, formats=["PNG"]):
    """Export a complete project with original image, depth map, and segmentation mask."""
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Create metadata
    metadata = {
        "original_image": f"{base_name}_original.{formats[0].lower()}",
        "depth_map": f"{base_name}_depth.{formats[0].lower()}",
        "segmentation_mask": f"{base_name}_segmentation.{formats[0].lower()}",
        "processed_images": []
    }
    
    # Export original image in all formats
    for format in formats:
        output_path = os.path.join(output_dir, f"{base_name}_original.{format.lower()}")
        export_image(image, output_path, format)
        
        if format != formats[0]:  # Add additional formats to metadata
            metadata["processed_images"].append({
                "type": "original",
                "format": format.lower(),
                "path": f"{base_name}_original.{format.lower()}"
            })
    
    # Export depth map
    depth_path = os.path.join(output_dir, f"{base_name}_depth.{formats[0].lower()}")
    export_depth_map(depth_map, depth_path, formats[0])
    
    # Export segmentation mask
    segmentation_path = os.path.join(output_dir, f"{base_name}_segmentation.{formats[0].lower()}")
    export_segmentation_mask(segmentation_mask, segmentation_path, formats[0])
    
    # Save metadata
    metadata_path = os.path.join(output_dir, f"{base_name}_metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    
    return metadata

def export_processed_image(original_image, processed_image, output_dir, base_name, 
                          formats=["PNG"], quality=95, dpi=(300, 300), 
                          include_original=True):
    """Export processed image in multiple formats."""
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Create metadata
    metadata = {
        "processed_image": f"{base_name}.{formats[0].lower()}",
        "additional_formats": []
    }
    
    # Export processed image in all formats
    for format in formats:
        output_path = os.path.join(output_dir, f"{base_name}.{format.lower()}")
        export_image(processed_image, output_path, format, quality, dpi)
        
        if format != formats[0]:  # Add additional formats to metadata
            metadata["additional_formats"].append({
                "format": format.lower(),
                "path": f"{base_name}.{format.lower()}"
            })
    
    # Export original image if requested
    if include_original:
        original_path = os.path.join(output_dir, f"{base_name}_original.{formats[0].lower()}")
        export_image(original_image, original_path, formats[0], quality, dpi)
        metadata["original_image"] = f"{base_name}_original.{formats[0].lower()}"
    
    # Save metadata
    metadata_path = os.path.join(output_dir, f"{base_name}_metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    
    return metadata

def main():
    parser = argparse.ArgumentParser(description="Export utilities for AI Text Behind Image")
    
    parser.add_argument("--image", required=True, help="Path to the input image")
    parser.add_argument("--output", required=True, help="Output path")
    parser.add_argument("--format", default="PNG", help="Output format (PNG, JPEG, WEBP, TIFF)")
    parser.add_argument("--quality", type=int, default=95, help="Output quality (for JPEG and WEBP)")
    parser.add_argument("--dpi", type=int, default=300, help="Output DPI")
    
    args = parser.parse_args()
    
    # Load image
    try:
        image = Image.open(args.image)
    except Exception as e:
        print(f"Error loading image: {e}")
        return 1
    
    # Export image
    try:
        output_path = export_image(image, args.output, args.format, args.quality, (args.dpi, args.dpi))
        print(f"Image exported to {output_path}")
    except Exception as e:
        print(f"Error exporting image: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())