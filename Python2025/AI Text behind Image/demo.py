import streamlit as st
import os
import sys
import requests
from PIL import Image
import io
import tempfile

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our modules
from ai_models import ModelFactory
from text_renderer import AdvancedTextRenderer
from image_utils import visualize_depth_map

# Download a sample image if none is provided
def get_sample_image():
    # URL for a sample image with clear foreground/background separation
    sample_image_url = "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80"
    
    try:
        response = requests.get(sample_image_url)
        image = Image.open(io.BytesIO(response.content))
        
        # Save the image to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            image.save(tmp_file, format='JPEG')
            return tmp_file.name
    except Exception as e:
        st.error(f"Error downloading sample image: {e}")
        return None

# Main demo function
def run_demo():
    st.title("AI Text Behind Image - Demo")
    st.write("This demo shows how the application works with a sample image.")
    
    # Get sample image
    sample_image_path = get_sample_image()
    
    if not sample_image_path:
        st.error("Could not load sample image. Please try again.")
        return
    
    # Load the image
    image = Image.open(sample_image_path)
    
    # Display the original image
    st.subheader("Original Image")
    st.image(image, use_column_width=True)
    
    # Load models
    with st.spinner("Loading AI models..."):
        depth_model = ModelFactory.get_depth_model()
        segmentation_model = ModelFactory.get_segmentation_model()
    
    # Process the image
    with st.spinner("Analyzing image depth and segmentation..."):
        # Get depth map
        depth_map = depth_model.predict(image)
        
        # Get segmentation mask
        segmentation_mask = segmentation_model.predict(image)
        
        # Visualize depth map
        depth_visualization = visualize_depth_map(depth_map)
    
    # Display depth map
    st.subheader("Depth Map")
    st.image(depth_visualization, use_column_width=True)
    st.write("Lighter areas are further away, darker areas are closer to the camera.")
    
    # Text input
    text_input = st.text_input("Enter text to place in the image", "Mountain Adventure")
    
    # Text customization
    col1, col2 = st.columns(2)
    
    with col1:
        font_size = st.slider("Font Size", 20, 80, 40)
        color = st.color_picker("Text Color", "#FFFFFF")
    
    with col2:
        perspective = st.slider("Perspective Effect", 0.0, 1.0, 0.2, 0.1)
        shadow_strength = st.slider("Shadow Strength", 0.0, 1.0, 0.5, 0.1)
    
    # Convert hex color to RGB
    color_rgb = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    
    # Render text with effects
    if st.button("Generate Image with Text"):
        with st.spinner("Rendering text with effects..."):
            # Create text renderer
            renderer = AdvancedTextRenderer()
            
            # Set up effects
            effects = {
                'perspective': perspective,
                'shadow': True,
                'shadow_strength': shadow_strength,
                'lighting_adaptation': True,
                'depth_threshold': 0.5
            }
            
            # Render text with depth awareness
            result_image = renderer.render_text_with_depth(
                image, text_input, depth_map, 
                font_name="arial.ttf", font_size=font_size,
                color=color_rgb, opacity=0.9, effects=effects
            )
            
            # Display result
            st.subheader("Result with Text")
            st.image(result_image, use_column_width=True)
            
            # Save the result to a temporary file for download
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                result_image.save(tmp_file, format='PNG')
                
                # Create download button
                with open(tmp_file.name, "rb") as file:
                    btn = st.download_button(
                        label="Download Result",
                        data=file,
                        file_name="text_behind_image_result.png",
                        mime="image/png"
                    )

# Run the demo
if __name__ == "__main__":
    run_demo()