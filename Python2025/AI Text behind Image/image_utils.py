import cv2
import numpy as np
import torch
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from skimage import segmentation, morphology
from torchvision import transforms
import matplotlib.pyplot as plt

# Helper function to convert PIL Image to numpy array and back
def pil_to_numpy(pil_image):
    """Convert PIL Image to numpy array."""
    return np.array(pil_image)

def numpy_to_pil(numpy_image):
    """Convert numpy array to PIL Image."""
    return Image.fromarray(numpy_image.astype(np.uint8))

# Image enhancement functions
def enhance_image(image, brightness=1.0, contrast=1.0, sharpness=1.0):
    """Apply basic image enhancements."""
    if not isinstance(image, Image.Image):
        image = numpy_to_pil(image)
    
    # Apply enhancements
    if brightness != 1.0:
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(brightness)
    
    if contrast != 1.0:
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(contrast)
    
    if sharpness != 1.0:
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(sharpness)
    
    return image

# Advanced text rendering functions
def create_text_mask(size, text, font, position, perspective=0.0):
    """Create a text mask with optional perspective effect."""
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    
    # Draw text on mask
    draw.text(position, text, font=font, fill=255)
    
    # Apply perspective if requested
    if perspective > 0:
        # Convert to numpy for perspective transformation
        mask_np = np.array(mask)
        
        # Calculate perspective transformation points
        h, w = mask_np.shape
        perspective_factor = perspective * w / 10
        
        # Source points (rectangle)
        src_points = np.float32([
            [0, 0],
            [w, 0],
            [w, h],
            [0, h]
        ])
        
        # Destination points (trapezoid for perspective)
        dst_points = np.float32([
            [perspective_factor, 0],
            [w - perspective_factor, 0],
            [w, h],
            [0, h]
        ])
        
        # Calculate transformation matrix
        matrix = cv2.getPerspectiveTransform(src_points, dst_points)
        
        # Apply transformation
        transformed_mask = cv2.warpPerspective(
            mask_np, 
            matrix, 
            (w, h),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=0
        )
        
        # Convert back to PIL
        mask = Image.fromarray(transformed_mask)
    
    return mask

def apply_lighting_from_image(text_image, source_image, region=None, adaptation_strength=0.5):
    """Adapt text lighting based on the source image lighting."""
    if region is None:
        # Use the entire image
        region = (0, 0, source_image.width, source_image.height)
    
    # Extract the region to analyze lighting
    region_img = source_image.crop(region)
    region_np = np.array(region_img)
    
    # Calculate lighting characteristics
    if len(region_np.shape) == 3 and region_np.shape[2] >= 3:
        # Convert to grayscale for brightness calculation
        if region_np.shape[2] == 4:  # RGBA
            gray_region = cv2.cvtColor(region_np, cv2.COLOR_RGBA2GRAY)
        else:  # RGB
            gray_region = cv2.cvtColor(region_np, cv2.COLOR_RGB2GRAY)
            
        # Calculate average brightness and contrast
        avg_brightness = np.mean(gray_region) / 255.0
        contrast = np.std(gray_region) / 255.0
        
        # Adjust text brightness and contrast based on background
        brightness_factor = 1.0
        contrast_factor = 1.0
        
        if avg_brightness > 0.7:  # Bright background
            brightness_factor = 1.0 - (adaptation_strength * 0.5)  # Darken text
            contrast_factor = 1.0 + (adaptation_strength * 0.3)  # Increase contrast
        elif avg_brightness < 0.3:  # Dark background
            brightness_factor = 1.0 + (adaptation_strength * 0.5)  # Brighten text
            contrast_factor = 1.0 + (adaptation_strength * 0.3)  # Increase contrast
        
        # Apply adjustments
        enhancer = ImageEnhance.Brightness(text_image)
        text_image = enhancer.enhance(brightness_factor)
        
        enhancer = ImageEnhance.Contrast(text_image)
        text_image = enhancer.enhance(contrast_factor)
    
    return text_image

# Shadow and glow effects
def add_shadow(image, mask, offset=(5, 5), radius=5, shadow_color=(0, 0, 0, 128)):
    """Add a shadow effect using the text mask."""
    # Create shadow image
    shadow = Image.new('RGBA', image.size, (0, 0, 0, 0))
    shadow.paste(shadow_color, offset, mask)
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=radius))
    
    # Composite shadow with image
    return Image.alpha_composite(image.convert('RGBA'), shadow)

def add_glow(image, mask, radius=10, glow_color=(255, 255, 255, 75)):
    """Add a glow effect using the text mask."""
    # Create glow image
    glow = Image.new('RGBA', image.size, (0, 0, 0, 0))
    glow.paste(glow_color, (0, 0), mask)
    glow = glow.filter(ImageFilter.GaussianBlur(radius=radius))
    
    # Composite glow with image
    return Image.alpha_composite(image.convert('RGBA'), glow)

# Depth map visualization and processing
def normalize_depth_map(depth_map):
    """Normalize depth map to 0-1 range."""
    depth_min = depth_map.min()
    depth_max = depth_map.max()
    
    if depth_max > depth_min:
        normalized = (depth_map - depth_min) / (depth_max - depth_min)
    else:
        normalized = np.zeros_like(depth_map)
    
    return normalized

def visualize_depth_map(depth_map, colormap='viridis'):
    """Create a colored visualization of a depth map."""
    # Normalize depth map
    normalized_depth = normalize_depth_map(depth_map)
    
    # Apply colormap
    cmap = plt.get_cmap(colormap)
    colored_depth = cmap(normalized_depth)
    
    # Convert to 8-bit RGB
    colored_depth_rgb = (colored_depth[:, :, :3] * 255).astype(np.uint8)
    
    return colored_depth_rgb

def create_depth_layers(depth_map, num_layers=3):
    """Segment depth map into discrete layers."""
    normalized_depth = normalize_depth_map(depth_map)
    
    # Create thresholds for layers
    thresholds = np.linspace(0, 1, num_layers + 1)
    
    # Initialize layers
    layers = []
    
    # Create each layer mask
    for i in range(num_layers):
        lower = thresholds[i]
        upper = thresholds[i + 1]
        
        # Create mask for this depth range
        layer_mask = (normalized_depth >= lower) & (normalized_depth < upper)
        
        # Clean up the mask with morphological operations
        layer_mask = morphology.binary_closing(layer_mask, morphology.disk(3))
        layer_mask = morphology.binary_opening(layer_mask, morphology.disk(2))
        
        layers.append(layer_mask)
    
    return layers

# Text placement functions
def find_optimal_text_regions(image, depth_map, min_region_size=1000, aspect_ratio_range=(1.5, 10)):
    """Find regions suitable for text placement based on depth and size."""
    # Normalize depth map
    normalized_depth = normalize_depth_map(depth_map)
    
    # Create depth layers
    layers = create_depth_layers(normalized_depth, num_layers=5)
    
    # Find potential regions in middle layers (not foreground or background)
    potential_regions = []
    
    for layer_idx in range(1, len(layers) - 1):  # Skip foreground and background layers
        layer_mask = layers[layer_idx]
        
        # Find connected components
        labeled_mask, num_labels = segmentation.label(layer_mask, return_num=True)
        
        for label in range(1, num_labels + 1):
            region_mask = labeled_mask == label
            area = np.sum(region_mask)
            
            # Only consider regions large enough
            if area >= min_region_size:
                rows, cols = np.where(region_mask)
                min_row, max_row = np.min(rows), np.max(rows)
                min_col, max_col = np.min(cols), np.max(cols)
                
                # Calculate region properties
                width = max_col - min_col
                height = max_row - min_row
                aspect_ratio = width / height if height > 0 else 0
                
                # Check if aspect ratio is suitable for text
                if aspect_ratio_range[0] <= aspect_ratio <= aspect_ratio_range[1]:
                    # Calculate depth consistency (lower is better)
                    depth_values = normalized_depth[region_mask]
                    depth_variance = np.var(depth_values)
                    
                    # Calculate region centrality (how close to image center)
                    img_center_y, img_center_x = np.array(image.size[::-1]) / 2
                    region_center_y = (min_row + max_row) / 2
                    region_center_x = (min_col + max_col) / 2
                    
                    distance_from_center = np.sqrt(
                        (region_center_x - img_center_x) ** 2 + 
                        (region_center_y - img_center_y) ** 2
                    )
                    centrality = 1 - (distance_from_center / np.sqrt(img_center_x ** 2 + img_center_y ** 2))
                    
                    # Calculate overall score (higher is better)
                    score = (area / min_region_size) * centrality * (1 - depth_variance)
                    
                    potential_regions.append({
                        'bbox': (min_col, min_row, max_col, max_row),
                        'area': area,
                        'aspect_ratio': aspect_ratio,
                        'depth_variance': depth_variance,
                        'centrality': centrality,
                        'score': score,
                        'layer': layer_idx
                    })
    
    # Sort regions by score (highest first)
    potential_regions.sort(key=lambda x: x['score'], reverse=True)
    
    return potential_regions