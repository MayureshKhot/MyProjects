import streamlit as st
import cv2
import numpy as np
import torch
import os
import tempfile
from PIL import Image, ImageDraw, ImageFont
from skimage import segmentation
from torchvision import transforms
from transformers import pipeline
import matplotlib.pyplot as plt
from io import BytesIO

# Set page configuration
st.set_page_config(
    page_title="AI Text Behind Image",
    page_icon="🖼️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load models and initialize components
@st.cache_resource
def load_models():
    # Load segmentation model (MiDaS for depth estimation)
    depth_estimator = pipeline("depth-estimation")
    return depth_estimator

# Process image to get depth map
def get_depth_map(image):
    depth_estimator = load_models()
    depth_result = depth_estimator(image)
    depth_map = depth_result["depth"]
    return depth_map

# Find optimal text placement zones
def find_text_placement_zones(depth_map, threshold=0.5):
    # Normalize depth map
    normalized_depth = (depth_map - depth_map.min()) / (depth_map.max() - depth_map.min())
    
    # Find regions with medium depth values (between foreground and background)
    mask = (normalized_depth > threshold - 0.2) & (normalized_depth < threshold + 0.2)
    
    # Find connected regions in the mask
    labeled_mask, num_labels = segmentation.label(mask, return_num=True)
    
    # Find the largest connected region
    if num_labels > 0:
        largest_region_label = np.argmax([np.sum(labeled_mask == i) for i in range(1, num_labels + 1)]) + 1
        placement_zone = labeled_mask == largest_region_label
        
        # Find the bounding box of the placement zone
        rows, cols = np.where(placement_zone)
        if len(rows) > 0 and len(cols) > 0:
            min_row, max_row = np.min(rows), np.max(rows)
            min_col, max_col = np.min(cols), np.max(cols)
            return (min_col, min_row, max_col, max_row)
    
    # Default to center of the image if no suitable zone found
    h, w = depth_map.shape
    return (w//4, h//3, 3*w//4, 2*h//3)

# Render text with perspective and lighting
def render_text_with_effects(image, text, placement_zone, font_name, font_size, color, opacity):
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
    
    # Add shadow for depth effect
    shadow_offset = max(1, font_size // 15)
    shadow_color = (0, 0, 0, int(opacity * 128))
    draw.text((text_x + shadow_offset, text_y + shadow_offset), text, font=font, fill=shadow_color)
    
    # Draw the main text
    text_color = (*color, int(opacity * 255))
    draw.text((text_x, text_y), text, font=font, fill=text_color)
    
    # Composite the text overlay with the original image
    result = Image.alpha_composite(image.convert('RGBA'), text_overlay)
    return result

# Main application
def main():
    st.title("AI Text Behind Image")
    st.write("Upload an image and add text between foreground and background elements with realistic depth perception.")
    
    # Sidebar for controls
    with st.sidebar:
        st.header("Text Customization")
        text_input = st.text_input("Enter your text", "Your text here")
        font_size = st.slider("Font Size", 10, 100, 40)
        opacity = st.slider("Opacity", 0.1, 1.0, 0.9, 0.1)
        color = st.color_picker("Text Color", "#FFFFFF")
        depth_threshold = st.slider("Depth Threshold", 0.1, 0.9, 0.5, 0.1)
        
        # Convert hex color to RGB
        color_rgb = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        
        # Font selection (limited options for simplicity)
        font_options = ["arial.ttf", "times.ttf", "calibri.ttf", "verdana.ttf"]
        font_name = st.selectbox("Font", font_options, index=0)
    
    # Image upload
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png", "webp"])
    
    if uploaded_file is not None:
        # Display original image
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Original Image")
            image = Image.open(uploaded_file)
            st.image(image, use_column_width=True)
        
        # Process image
        with st.spinner("Analyzing image depth..."):
            # Get depth map
            depth_map = get_depth_map(image)
            
            # Find optimal text placement zone
            placement_zone = find_text_placement_zones(depth_map, depth_threshold)
            
            # Render text with effects
            result_image = render_text_with_effects(
                image, text_input, placement_zone, font_name, font_size, color_rgb, opacity
            )
        
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

if __name__ == "__main__":
    main()