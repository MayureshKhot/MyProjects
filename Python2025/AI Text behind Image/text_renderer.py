import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageChops
import math

class TextRenderer:
    def __init__(self):
        self.default_font = "arial.ttf"
        self.default_font_size = 40
    
    def render_text(self, image, text, placement_zone, font_name=None, font_size=None, 
                    color=(255, 255, 255), opacity=0.9, effects=None):
        """Render text on an image with various effects.
        
        Args:
            image: PIL Image or numpy array
            text: Text to render
            placement_zone: Tuple (x1, y1, x2, y2) defining the text placement area
            font_name: Font file name
            font_size: Font size
            color: RGB color tuple
            opacity: Text opacity (0.0 to 1.0)
            effects: Dictionary of effects to apply
        
        Returns:
            PIL Image with rendered text
        """
        # Convert to PIL Image if it's not already
        if not isinstance(image, Image.Image):
            image = Image.fromarray(image)
        
        # Create a transparent overlay for the text
        text_overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
        
        # Set default values if not provided
        font_name = font_name or self.default_font
        font_size = font_size or self.default_font_size
        effects = effects or {}
        
        # Load font
        try:
            font = ImageFont.truetype(font_name, font_size)
        except IOError:
            font = ImageFont.load_default()
        
        # Get text dimensions
        draw = ImageDraw.Draw(text_overlay)
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        # Calculate text position within the placement zone
        # Ensure placement_zone values are Python integers to avoid NumPy array ambiguity
        x1, y1, x2, y2 = map(int, placement_zone)
        zone_width = x2 - x1
        zone_height = y2 - y1
        
        # Check if text fits in the zone
        if text_width > zone_width or text_height > zone_height:
            # Scale down font size to fit
            scale_factor = min(zone_width / text_width, zone_height / text_height) * 0.9
            font_size = int(font_size * scale_factor)
            try:
                font = ImageFont.truetype(font_name, font_size)
            except IOError:
                font = ImageFont.load_default()
            
            # Recalculate text dimensions
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
        
        # Center text in the placement zone
        text_x = x1 + (zone_width - text_width) // 2
        text_y = y1 + (zone_height - text_height) // 2
        
        # Apply effects based on the provided effects dictionary
        result_image = self._apply_effects(image, text_overlay, text, font, (text_x, text_y), 
                                          color, opacity, effects)
        
        return result_image
    
    def _apply_effects(self, image, text_overlay, text, font, position, color, opacity, effects):
        """Apply various effects to the text."""
        draw = ImageDraw.Draw(text_overlay)
        text_x, text_y = position
        
        # Convert color to RGBA
        if len(color) == 3:
            color_rgba = (*color, int(opacity * 255))
        else:
            color_rgba = color
        
        # Apply perspective effect if requested
        if effects.get('perspective', 0) > 0:
            text_overlay = self._apply_perspective(text_overlay, text, font, position, 
                                                 color_rgba, effects['perspective'])
        else:
            # Apply shadow if requested
            if effects.get('shadow', True):
                shadow_offset = effects.get('shadow_offset', max(1, font.size // 15))
                shadow_blur = effects.get('shadow_blur', 5)
                shadow_color = effects.get('shadow_color', (0, 0, 0, int(opacity * 128)))
                
                # Create shadow text
                shadow_pos = (text_x + shadow_offset, text_y + shadow_offset)
                draw.text(shadow_pos, text, font=font, fill=shadow_color)
                
                # Apply blur to shadow
                if shadow_blur > 0:
                    text_overlay = text_overlay.filter(ImageFilter.GaussianBlur(radius=shadow_blur))
                    
                    # Redraw the overlay for the main text
                    draw = ImageDraw.Draw(text_overlay)
            
            # Apply glow if requested
            if effects.get('glow', False):
                glow_radius = effects.get('glow_radius', 10)
                glow_color = effects.get('glow_color', (*color, int(opacity * 50)))
                
                # Create glow mask
                glow_mask = Image.new('L', text_overlay.size, 0)
                glow_draw = ImageDraw.Draw(glow_mask)
                glow_draw.text(position, text, font=font, fill=255)
                
                # Apply blur to glow mask
                glow_mask = glow_mask.filter(ImageFilter.GaussianBlur(radius=glow_radius))
                
                # Apply glow
                for i in range(3):
                    text_overlay.paste(glow_color, (0, 0), glow_mask)
            
            # Draw the main text
            draw.text(position, text, font=font, fill=color_rgba)
        
        # Apply 3D effect if requested
        if effects.get('3d', False):
            depth = effects.get('3d_depth', 5)
            depth_color = effects.get('3d_color', (0, 0, 0, int(opacity * 200)))
            
            # Create layers for 3D effect
            for i in range(1, depth + 1):
                offset = i
                draw.text((text_x - offset, text_y + offset), text, font=font, fill=depth_color)
            
            # Redraw the main text on top
            draw.text(position, text, font=font, fill=color_rgba)
        
        # Apply lighting adaptation if requested
        if effects.get('lighting_adaptation', False):
            text_overlay = self._adapt_lighting(image, text_overlay, placement_zone=effects.get('placement_zone'))
        
        # Apply blur if requested
        if effects.get('blur', 0) > 0:
            text_overlay = text_overlay.filter(ImageFilter.GaussianBlur(radius=effects.get('blur')))
        
        # Composite the text overlay with the original image
        result = Image.alpha_composite(image.convert('RGBA'), text_overlay)
        return result
    
    def _apply_perspective(self, text_overlay, text, font, position, color, perspective_amount):
        """Apply perspective transformation to text."""
        # Create a new image for the text with perspective
        text_x, text_y = position
        text_bbox = ImageDraw.Draw(text_overlay).textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        # Add padding around text
        padding = max(20, int(text_height * 0.2))
        text_img = Image.new('RGBA', (text_width + padding * 2, text_height + padding * 2), (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_img)
        text_draw.text((padding, padding), text, font=font, fill=color)
        
        # Calculate perspective transformation points
        width, height = text_img.size
        perspective_factor = perspective_amount * width / 10
        
        # Source points (rectangle)
        src_points = np.float32([
            [0, 0],
            [width, 0],
            [width, height],
            [0, height]
        ])
        
        # Destination points (trapezoid for perspective)
        dst_points = np.float32([
            [perspective_factor, 0],
            [width - perspective_factor, 0],
            [width, height],
            [0, height]
        ])
        
        # Calculate transformation matrix
        matrix = cv2.getPerspectiveTransform(src_points, dst_points)
        
        # Apply transformation
        text_img_np = np.array(text_img)
        transformed_text = cv2.warpPerspective(
            text_img_np, 
            matrix, 
            (width, height),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(0, 0, 0, 0)
        )
        
        # Convert back to PIL and paste onto the overlay
        transformed_text_pil = Image.fromarray(transformed_text)
        text_overlay.paste(transformed_text_pil, (text_x - padding, text_y - padding), transformed_text_pil)
        
        return text_overlay
    
    def _adapt_lighting(self, image, text_overlay, placement_zone=None):
        """Adapt text lighting based on the background image."""
        if placement_zone is None:
            # Use the entire image
            placement_zone = (0, 0, image.width, image.height)
        
        # Extract the region to analyze lighting
        region = image.crop(placement_zone)
        region_np = np.array(region)
        
        # Calculate average brightness in the region
        if len(region_np.shape) == 3 and region_np.shape[2] >= 3:
            # Convert to grayscale for brightness calculation
            if region_np.shape[2] == 4:  # RGBA
                gray_region = cv2.cvtColor(region_np, cv2.COLOR_RGBA2GRAY)
            else:  # RGB
                gray_region = cv2.cvtColor(region_np, cv2.COLOR_RGB2GRAY)
            
            avg_brightness = np.mean(gray_region) / 255.0
            
            # Adjust text brightness based on background
            brightness_factor = 1.0
            # Use direct comparison since avg_brightness is a scalar
            if avg_brightness > 0.7:  # Bright background
                brightness_factor = 0.7  # Darken text
            elif avg_brightness < 0.3:  # Dark background
                brightness_factor = 1.3  # Brighten text
            
            # Apply brightness adjustment
            enhancer = ImageEnhance.Brightness(text_overlay)
            text_overlay = enhancer.enhance(brightness_factor)
        
        return text_overlay

class AdvancedTextRenderer(TextRenderer):
    """Extended text renderer with additional advanced effects."""
    
    def render_text_with_depth(self, image, text, depth_map, font_name=None, font_size=None,
                              color=(255, 255, 255), opacity=0.9, effects=None):
        """Render text with depth-aware effects.
        
        Args:
            image: PIL Image or numpy array
            text: Text to render
            depth_map: Depth map of the image
            font_name: Font file name
            font_size: Font size
            color: RGB color tuple
            opacity: Text opacity (0.0 to 1.0)
            effects: Dictionary of effects to apply
        
        Returns:
            PIL Image with rendered text
        """
        # Convert to PIL Image if it's not already
        if not isinstance(image, Image.Image):
            image = Image.fromarray(image)
        
        # Initialize effects dictionary if None
        effects = effects or {}
        
        # Find optimal placement zone based on depth map
        placement_zone = self._find_optimal_placement(depth_map, effects.get('depth_threshold', 0.5))
        
        # Ensure placement_zone values are Python integers to avoid NumPy array ambiguity
        if placement_zone is not None and len(placement_zone) == 4:
            placement_zone = tuple(map(int, placement_zone))
        
        # Add placement zone to effects
        effects['placement_zone'] = placement_zone
        
        # Add depth-aware effects
        if 'depth_aware_shadow' not in effects:
            effects['depth_aware_shadow'] = True
        
        # Render text with effects
        result = self.render_text(image, text, placement_zone, font_name, font_size, color, opacity, effects)
        
        return result
    
    def _find_optimal_placement(self, depth_map, threshold=0.5):
        """Find optimal text placement zone based on depth map."""
        # Normalize depth map
        depth_min = depth_map.min()
        depth_max = depth_map.max()
        normalized_depth = (depth_map - depth_min) / (depth_max - depth_min)
        
        # Find regions with medium depth values (between foreground and background)
        # Use explicit comparison to avoid ambiguity with boolean arrays
        lower_bound = threshold - 0.2
        upper_bound = threshold + 0.2
        mask = np.logical_and(normalized_depth > lower_bound, normalized_depth < upper_bound)
        
        # Find connected regions in the mask
        labeled_mask, num_labels = cv2.connectedComponents(mask.astype(np.uint8))
        
        # Find the largest connected region
        if num_labels > 1:  # 0 is background
            region_sizes = [np.sum(labeled_mask == i) for i in range(1, num_labels)]
            largest_region_label = np.argmax(region_sizes) + 1
            placement_zone = labeled_mask == largest_region_label
            
            # Find the bounding box of the placement zone
            rows, cols = np.where(placement_zone)
            # Use explicit comparison to avoid ambiguity with boolean arrays
            if len(rows) > 0 and len(cols) > 0:
                # Convert NumPy values to Python integers to avoid ambiguity
                min_row, max_row = int(np.min(rows)), int(np.max(rows))
                min_col, max_col = int(np.min(cols)), int(np.max(cols))
                return (min_col, min_row, max_col, max_row)
        
        # Default to center of the image if no suitable zone found
        h, w = depth_map.shape
        return (w//4, h//3, 3*w//4, 2*h//3)
    
    def apply_depth_aware_shadow(self, image, text_overlay, depth_map, text_position, text_size):
        """Apply shadow that adapts to the depth map."""
        # Extract depth values in the text region
        text_x, text_y = text_position
        text_width, text_height = text_size
        
        # Define the text region in the depth map
        region_x = max(0, text_x)
        region_y = max(0, text_y)
        region_width = min(text_width, depth_map.shape[1] - region_x)
        region_height = min(text_height, depth_map.shape[0] - region_y)
        
        # Use .any() to avoid ambiguity with boolean arrays
        if region_width <= 0 or region_height <= 0:
            return text_overlay
        
        # Extract depth in the region
        depth_region = depth_map[region_y:region_y+region_height, region_x:region_x+region_width]
        
        # Calculate average depth and gradient
        avg_depth = np.mean(depth_region)
        
        # Calculate gradient (simplified)
        # Use .all() to avoid ambiguity with boolean arrays
        if depth_region.shape[0] > 1 and depth_region.shape[1] > 1:
            gradient_y, gradient_x = np.gradient(depth_region)
            avg_gradient_x = np.mean(gradient_x)
            avg_gradient_y = np.mean(gradient_y)
        else:
            avg_gradient_x, avg_gradient_y = 0, 0
        
        # Determine shadow direction and strength based on depth gradient
        shadow_offset_x = int(avg_gradient_x * 20)  # Scale factor for visibility
        shadow_offset_y = int(avg_gradient_y * 20)
        
        # Ensure minimum shadow offset
        # Use .all() to avoid ambiguity with boolean arrays
        if np.abs(shadow_offset_x) < 2 and np.abs(shadow_offset_y) < 2:
            shadow_offset_x = 2
            shadow_offset_y = 2
        
        # Shadow strength based on depth
        depth_max = np.max(depth_map)
        # Use .any() to avoid ambiguity with boolean arrays
        if depth_max > 0:  # Avoid division by zero
            shadow_opacity = int(128 * (1 - avg_depth / depth_max))
        else:
            shadow_opacity = 128
        # Ensure shadow_opacity is a valid value
        shadow_opacity = max(50, min(200, shadow_opacity))  # Clamp to reasonable range
        
        # Create shadow
        shadow_overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow_overlay)
        
        # Extract text mask from text_overlay
        text_mask = text_overlay.split()[3]  # Alpha channel
        
        # Create shadow by offsetting the text mask
        shadow_overlay.paste((0, 0, 0, shadow_opacity), 
                            (shadow_offset_x, shadow_offset_y), 
                            text_mask)
        
        # Blur the shadow
        shadow_overlay = shadow_overlay.filter(ImageFilter.GaussianBlur(radius=3))
        
        # Composite shadow with original overlay
        result = Image.alpha_composite(shadow_overlay, text_overlay)
        
        return result