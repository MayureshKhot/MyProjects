import streamlit as st
import cv2
import numpy as np
import torch
import os
import tempfile
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from skimage import segmentation, morphology
from torchvision import transforms, models
from transformers import pipeline, AutoImageProcessor, AutoModelForDepthEstimation
import matplotlib.pyplot as plt
from io import BytesIO
import time

# Set page configuration
st.set_page_config(
    page_title="AI Text Behind Image - Advanced",
    page_icon="🖼️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load models and initialize components
@st.cache_resource
def load_models():
    # Load depth estimation model
    depth_processor = AutoImageProcessor.from_pretrained("Intel/dpt-large")
    depth_model = AutoModelForDepthEstimation.from_pretrained("Intel/dpt-large")
    
    # Load segmentation model (DeepLabV3)
    segmentation_model = models.segmentation.deeplabv3_resnet101(pretrained=True)
    segmentation_model.eval()
    
    return depth_processor, depth_model, segmentation_model

# Process image to get depth map
def get_depth_map(image, depth_processor, depth_model):
    # Convert PIL Image to numpy array if needed
    if isinstance(image, Image.Image):
        image_np = np.array(image)
    else:
        image_np = image
        
    # Prepare image for the model
    inputs = depth_processor(images=image_np, return_tensors="pt")
    
    with torch.no_grad():
        outputs = depth_model(**inputs)
        predicted_depth = outputs.predicted_depth
    
    # Interpolate to original size
    prediction = torch.nn.functional.interpolate(
        predicted_depth.unsqueeze(1),
        size=image_np.shape[:2],
        mode="bicubic",
        align_corners=False,
    ).squeeze()
    
    depth_map = prediction.numpy()
    return depth_map

# Segment image into foreground, midground, and background
def segment_image(image, segmentation_model):
    # Prepare image for the model
    preprocess = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    
    # Convert PIL Image to tensor
    if isinstance(image, Image.Image):
        input_tensor = preprocess(image)
    else:
        input_tensor = preprocess(Image.fromarray(image))
    
    input_batch = input_tensor.unsqueeze(0)
    
    with torch.no_grad():
        output = segmentation_model(input_batch)['out'][0]
    
    output_predictions = output.argmax(0).byte().numpy()
    
    return output_predictions

# Find optimal text placement zones using both depth and segmentation
def find_text_placement_zones(image, depth_map, segmentation_mask, threshold=0.5):
    # Normalize depth map
    normalized_depth = (depth_map - depth_map.min()) / (depth_map.max() - depth_map.min())
    
    # Create depth ranges for foreground, midground, and background
    foreground_mask = normalized_depth < (threshold - 0.2)
    background_mask = normalized_depth > (threshold + 0.2)
    midground_mask = ~(foreground_mask | background_mask)
    
    # Refine midground mask using segmentation information
    refined_midground = midground_mask & (segmentation_mask > 0)
    
    # Apply morphological operations to clean up the mask
    refined_midground = morphology.binary_dilation(refined_midground, morphology.disk(5))
    refined_midground = morphology.binary_erosion(refined_midground, morphology.disk(3))
    
    # Find connected regions in the refined mask
    labeled_mask, num_labels = segmentation.label(refined_midground, return_num=True)
    
    # Find suitable regions for text placement
    regions = []
    for i in range(1, num_labels + 1):
        region_mask = labeled_mask == i
        area = np.sum(region_mask)
        
        # Only consider regions large enough for text
        if area > 1000:  # Adjust threshold based on image size
            rows, cols = np.where(region_mask)
            min_row, max_row = np.min(rows), np.max(rows)
            min_col, max_col = np.min(cols), np.max(cols)
            
            # Calculate region properties
            width = max_col - min_col
            height = max_row - min_row
            aspect_ratio = width / height if height > 0 else 0
            
            # Only consider regions with suitable aspect ratio for text
            if 1.5 < aspect_ratio < 10 and width > 100 and height > 20:
                regions.append((min_col, min_row, max_col, max_row, area))
    
    # Sort regions by area (largest first)
    regions.sort(key=lambda x: x[4], reverse=True)
    
    if regions:
        # Return the largest suitable region
        return regions[0][:4]
    
    # Default to center of the image if no suitable zone found
    h, w = depth_map.shape
    return (w//4, h//3, 3*w//4, 2*h//3)

# Render text with perspective and lighting
def render_text_with_effects(image, text, placement_zone, font_name, font_size, color, opacity, 
                            perspective=0.2, lighting_adaptation=True, shadow_strength=0.5):
    # Convert to PIL Image if it's not already
    if not isinstance(image, Image.Image):
        image = Image.fromarray(image)
    
    # Create a transparent overlay for the text
    text_overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(text_overlay)
    
    # Load font
    try:
        font = ImageFont.truetype(font_name, font_size)
    except IOError:
        font = ImageFont.load_default()
    
    # Calculate text position within the placement zone
    x1, y1, x2, y2 = placement_zone
    text_width, text_height = draw.textbbox((0, 0), text, font=font)[2:]
    
    # Center text in the placement zone
    text_x = x1 + (x2 - x1 - text_width) // 2
    text_y = y1 + (y2 - y1 - text_height) // 2
    
    # Apply perspective transformation if requested
    if perspective > 0:
        # Create a new image for the text with perspective
        text_img = Image.new('RGBA', (text_width + 40, text_height + 40), (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_img)
        text_draw.text((20, 20), text, font=font, fill=(*color, 255))
        
        # Calculate perspective transformation points
        width, height = text_img.size
        perspective_factor = perspective * width / 10
        
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
        text_overlay.paste(transformed_text_pil, (text_x - 20, text_y - 20), transformed_text_pil)
    else:
        # Add shadow for depth effect
        shadow_offset = max(1, font_size // 15)
        shadow_color = (0, 0, 0, int(opacity * 255 * shadow_strength))
        draw.text((text_x + shadow_offset, text_y + shadow_offset), text, font=font, fill=shadow_color)
        
        # Draw the main text
        text_color = (*color, int(opacity * 255))
        draw.text((text_x, text_y), text, font=font, fill=text_color)
    
    # Apply lighting adaptation if requested
    if lighting_adaptation:
        # Extract the region around the text to analyze lighting
        region = image.crop(placement_zone)
        region_np = np.array(region)
        
        # Calculate average brightness in the region
        if len(region_np.shape) == 3 and region_np.shape[2] >= 3:
            # Convert to grayscale for brightness calculation
            gray_region = cv2.cvtColor(region_np, cv2.COLOR_RGB2GRAY)
            avg_brightness = np.mean(gray_region) / 255.0
            
            # Adjust text brightness based on background
            brightness_factor = 1.0
            if avg_brightness > 0.7:  # Bright background
                brightness_factor = 0.7  # Darken text
            elif avg_brightness < 0.3:  # Dark background
                brightness_factor = 1.3  # Brighten text
            
            # Apply brightness adjustment
            enhancer = ImageEnhance.Brightness(text_overlay)
            text_overlay = enhancer.enhance(brightness_factor)
    
    # Apply slight blur to blend with image
    text_overlay = text_overlay.filter(ImageFilter.GaussianBlur(radius=0.5))
    
    # Composite the text overlay with the original image
    result = Image.alpha_composite(image.convert('RGBA'), text_overlay)
    return result

# Visualize depth map
def visualize_depth_map(depth_map):
    # Normalize depth map for visualization
    normalized_depth = (depth_map - depth_map.min()) / (depth_map.max() - depth_map.min())
    
    # Create a colormap
    cmap = plt.cm.viridis
    colored_depth = cmap(normalized_depth)
    
    # Convert to PIL Image
    colored_depth_image = Image.fromarray((colored_depth[:, :, :3] * 255).astype(np.uint8))
    return colored_depth_image

# Main application
def main():
    st.title("AI Text Behind Image - Advanced")
    st.write("Upload an image and add text between foreground and background elements with realistic depth perception.")
    
    # Load models
    with st.spinner("Loading AI models..."):
        depth_processor, depth_model, segmentation_model = load_models()
    
    # Sidebar for controls
    with st.sidebar:
        st.header("Text Customization")
        text_input = st.text_input("Enter your text", "Your text here")
        font_size = st.slider("Font Size", 10, 100, 40)
        opacity = st.slider("Opacity", 0.1, 1.0, 0.9, 0.1)
        color = st.color_picker("Text Color", "#FFFFFF")
        depth_threshold = st.slider("Depth Threshold", 0.1, 0.9, 0.5, 0.1)
        
        st.header("Advanced Options")
        perspective_amount = st.slider("Perspective Effect", 0.0, 1.0, 0.2, 0.1)
        shadow_strength = st.slider("Shadow Strength", 0.0, 1.0, 0.5, 0.1)
        lighting_adaptation = st.checkbox("Adapt to Scene Lighting", True)
        show_depth_map = st.checkbox("Show Depth Map", False)
        
        # Convert hex color to RGB
        color_rgb = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        
        # Font selection (limited options for simplicity)
        font_options = ["arial.ttf", "times.ttf", "calibri.ttf", "verdana.ttf"]
        font_name = st.selectbox("Font", font_options, index=0)
    
    # Image upload
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png", "webp"])
    
    if uploaded_file is not None:
        # Display original image
        image = Image.open(uploaded_file)
        
        # Create columns for layout
        if show_depth_map:
            col1, col2, col3 = st.columns(3)
        else:
            col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Original Image")
            st.image(image, use_column_width=True)
        
        # Process image
        with st.spinner("Analyzing image depth and segmentation..."):
            # Get depth map
            depth_map = get_depth_map(image, depth_processor, depth_model)
            
            # Get segmentation mask
            segmentation_mask = segment_image(image, segmentation_model)
            
            # Find optimal text placement zone
            placement_zone = find_text_placement_zones(image, depth_map, segmentation_mask, depth_threshold)
            
            # Render text with effects
            result_image = render_text_with_effects(
                image, text_input, placement_zone, font_name, font_size, color_rgb, opacity,
                perspective_amount, lighting_adaptation, shadow_strength
            )
            
            # Visualize depth map if requested
            if show_depth_map:
                depth_visualization = visualize_depth_map(depth_map)
        
        # Display result
        with col2:
            st.subheader("Result with Text")
            st.image(result_image, use_column_width=True)
            
            # Export options
            st.subheader("Export Options")
            output_format = st.selectbox("Format", ["PNG", "JPEG", "WEBP"], index=0)
            quality = st.slider("Quality", 1, 100, 95) if output_format != "PNG" else None
            
            # Create download button
            buf = BytesIO()
            if output_format == "PNG":
                result_image.save(buf, format="PNG")
            elif output_format == "JPEG":
                result_image = result_image.convert("RGB")
                result_image.save(buf, format="JPEG", quality=quality)
            elif output_format == "WEBP":
                result_image.save(buf, format="WEBP", quality=quality)
            
            buf.seek(0)
            st.download_button(
                label=f"Download {output_format}",
                data=buf,
                file_name=f"text_behind_image.{output_format.lower()}",
                mime=f"image/{output_format.lower()}"
            )
        
        # Display depth map if requested
        if show_depth_map:
            with col3:
                st.subheader("Depth Map")
                st.image(depth_visualization, use_column_width=True)
                st.write("Darker areas are closer to the camera, lighter areas are further away.")

if __name__ == "__main__":
    main()