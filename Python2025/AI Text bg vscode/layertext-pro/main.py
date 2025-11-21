import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import io
from typing import Tuple, List, Optional

class ImageLayerProcessor:
    def __init__(self):
        self.original_image = None
        self.depth_map = None
        self.foreground_mask = None
        self.background_mask = None
    
    def load_image(self, uploaded_file) -> Image.Image:
        """Load and preprocess the uploaded image"""
        image = Image.open(uploaded_file)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        return image
    
    def create_advanced_depth_map(self, image: Image.Image) -> np.ndarray:
        """Create sophisticated depth map using multiple CV techniques"""
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        
        # 1. Edge-based depth estimation
        edges = cv2.Canny(gray, 50, 150)
        dist_from_edges = cv2.distanceTransform(255 - edges, cv2.DIST_L2, 5)
        cv2.normalize(dist_from_edges, dist_from_edges, 0, 1, cv2.NORM_MINMAX)
        
        # 2. Gradient-based depth (objects with strong gradients are usually closer)
        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        gradient_magnitude = gradient_magnitude / np.max(gradient_magnitude)
        
        # 3. Contrast-based depth (higher contrast areas are usually closer)
        kernel = np.ones((9,9), np.float32) / 81
        smoothed = cv2.filter2D(gray.astype(np.float32), -1, kernel)
        contrast = np.abs(gray.astype(np.float32) - smoothed)
        contrast = contrast / np.max(contrast)
        
        # 4. Color saturation depth (more saturated = closer, typically)
        hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
        saturation = hsv[:,:,1].astype(np.float32) / 255.0
        
        # Combine all depth cues
        depth_map = (
            dist_from_edges * 0.25 +      # Areas away from edges = background
            (1 - gradient_magnitude) * 0.25 +  # Low gradient = background
            (1 - contrast) * 0.25 +       # Low contrast = background
            (1 - saturation) * 0.25       # Low saturation = background
        )
        
        # Apply strong smoothing for clean layer separation
        depth_map = cv2.GaussianBlur(depth_map, (31, 31), 0)
        
        return depth_map
    
    def create_layer_masks(self, image: Image.Image, depth_map: np.ndarray) -> dict:
        """Create precise foreground and background masks"""
        # Use adaptive thresholding based on depth distribution
        foreground_threshold = np.percentile(depth_map, 35)  # Bottom 35% = foreground
        background_threshold = np.percentile(depth_map, 70)   # Top 30% = background
        
        # Create initial masks
        foreground_mask = depth_map <= foreground_threshold
        background_mask = depth_map >= background_threshold
        middle_mask = (depth_map > foreground_threshold) & (depth_map < background_threshold)
        
        # Refine masks using morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
        
        # Clean up foreground mask
        foreground_mask = foreground_mask.astype(np.uint8) * 255
        foreground_mask = cv2.morphologyEx(foreground_mask, cv2.MORPH_CLOSE, kernel)
        foreground_mask = cv2.morphologyEx(foreground_mask, cv2.MORPH_OPEN, kernel)
        
        # Clean up background mask  
        background_mask = background_mask.astype(np.uint8) * 255
        background_mask = cv2.morphologyEx(background_mask, cv2.MORPH_CLOSE, kernel)
        background_mask = cv2.morphologyEx(background_mask, cv2.MORPH_OPEN, kernel)
        
        # Convert back to boolean
        foreground_mask = foreground_mask > 127
        background_mask = background_mask > 127
        
        # Update middle mask
        middle_mask = ~(foreground_mask | background_mask)
        
        return {
            'foreground': foreground_mask,
            'background': background_mask,
            'middle': middle_mask,
            'depth_map': depth_map
        }
    
    def extract_layers(self, image: Image.Image, masks: dict) -> dict:
        """Extract foreground and background as separate images"""
        img_array = np.array(image)
        
        # Create foreground image (with transparency for non-foreground areas)
        foreground_img = img_array.copy()
        foreground_alpha = masks['foreground'].astype(np.uint8) * 255
        foreground_rgba = np.dstack([foreground_img, foreground_alpha])
        
        # Create background image by inpainting foreground areas
        background_img = self._inpaint_foreground_areas(img_array, masks['foreground'])
        
        return {
            'foreground': Image.fromarray(foreground_rgba, 'RGBA'),
            'background': Image.fromarray(background_img, 'RGB'),
            'original': image
        }
    
    def _inpaint_foreground_areas(self, image: np.ndarray, foreground_mask: np.ndarray) -> np.ndarray:
        """Fill foreground areas with inpainted background content"""
        try:
            # Convert mask for OpenCV inpainting (needs to be uint8)
            mask_for_inpaint = foreground_mask.astype(np.uint8) * 255
            
            # Convert image to BGR for OpenCV
            img_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            # Use OpenCV inpainting to fill foreground areas
            inpainted_bgr = cv2.inpaint(
                img_bgr,
                mask_for_inpaint,
                inpaintRadius=10,
                flags=cv2.INPAINT_TELEA
            )
            
            # Convert back to RGB
            inpainted_rgb = cv2.cvtColor(inpainted_bgr, cv2.COLOR_BGR2RGB)
            
            return inpainted_rgb
            
        except Exception as e:
            # Fallback: simple background estimation using median blur
            print(f"Inpainting failed, using fallback method: {e}")
            result = image.copy()
            
            # Apply heavy blur to create background approximation
            blurred = cv2.GaussianBlur(image, (51, 51), 0)
            
            # Replace foreground areas with blurred version
            mask_3d = np.stack([foreground_mask] * 3, axis=-1)
            result = np.where(mask_3d, blurred, result)
            
            return result
    
    def find_optimal_text_zones(self, masks: dict, image_size: Tuple[int, int]) -> List[dict]:
        """Find optimal zones for text placement in middle layer"""
        middle_mask = masks['middle']
        depth_map = masks['depth_map']
        height, width = middle_mask.shape
        
        # Create zones in middle layer areas
        zones = []
        grid_size = 3
        
        for i in range(grid_size):
            for j in range(grid_size):
                y_start = i * height // grid_size
                y_end = (i + 1) * height // grid_size
                x_start = j * width // grid_size  
                x_end = (j + 1) * width // grid_size
                
                # Analyze this zone
                zone_middle = middle_mask[y_start:y_end, x_start:x_end]
                zone_depth = depth_map[y_start:y_end, x_start:x_end]
                
                # Calculate metrics
                middle_coverage = np.sum(zone_middle) / zone_middle.size
                avg_depth = np.mean(zone_depth)
                depth_consistency = 1.0 - np.std(zone_depth)
                
                # Only consider zones with good middle layer coverage
                if middle_coverage > 0.4:
                    score = middle_coverage * 0.6 + depth_consistency * 0.4
                    
                    zones.append({
                        'x': x_start + (x_end - x_start) // 2,
                        'y': y_start + (y_end - y_start) // 2,
                        'depth': avg_depth,
                        'score': score,
                        'coverage': middle_coverage,
                        'region': f"Zone {i+1}-{j+1}",
                        'bounds': (x_start, y_start, x_end, y_end)
                    })
        
        # Sort by score
        zones.sort(key=lambda x: x['score'], reverse=True)
        return zones

class LayerTextRenderer:
    @staticmethod
    def render_text_between_layers(layers: dict, text: str, position: Tuple[int, int],
                                 font_size: int = 48, color: str = "white",
                                 shadow_intensity: float = 0.8) -> Image.Image:
        """Render text between foreground and background layers"""
        
        background_img = layers['background']
        foreground_img = layers['foreground']
        
        # Create text layer
        text_layer = Image.new('RGBA', background_img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(text_layer)
        
        # Load font
        font = LayerTextRenderer._load_best_font(font_size)
        
        x, y = position
        
        # Add shadow for depth
        if shadow_intensity > 0:
            shadow_offset = 4
            shadow_alpha = int(150 * shadow_intensity)
            
            # Multi-layer shadow for more realism
            for i, offset_mult in enumerate([1.5, 1.0, 0.5]):
                shadow_x = x + int(shadow_offset * offset_mult)
                shadow_y = y + int(shadow_offset * offset_mult * 1.2)
                alpha = int(shadow_alpha * (1.0 - i * 0.3))
                shadow_color = f"rgba(0,0,0,{alpha})"
                draw.text((shadow_x, shadow_y), text, fill=shadow_color, font=font)
        
        # Draw main text
        draw.text((x, y), text, fill=color, font=font)
        
        # Layer composition: Background + Text + Foreground
        # 1. Start with background
        result = background_img.copy().convert('RGBA')
        
        # 2. Composite text onto background
        result = Image.alpha_composite(result, text_layer)
        
        # 3. Composite foreground on top (this is key!)
        result = Image.alpha_composite(result, foreground_img)
        
        return result.convert('RGB')
    
    @staticmethod  
    def _load_best_font(font_size: int):
        """Load the best available font"""
        try:
            import platform
            system = platform.system()
            
            font_paths = []
            if system == "Windows":
                font_paths = [
                    "C:/Windows/Fonts/arial.ttf",
                    "C:/Windows/Fonts/calibri.ttf", 
                    "C:/Windows/Fonts/segoeui.ttf"
                ]
            elif system == "Darwin":
                font_paths = [
                    "/System/Library/Fonts/Helvetica.ttc",
                    "/System/Library/Fonts/Arial.ttf"
                ]
            else:
                font_paths = [
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
                ]
            
            for font_path in font_paths:
                try:
                    return ImageFont.truetype(font_path, font_size)
                except:
                    continue
                    
        except:
            pass
            
        return ImageFont.load_default()

def create_layer_visualization(masks: dict, original_image: Image.Image) -> Image.Image:
    """Create visualization showing the different layers"""
    img_array = np.array(original_image)
    
    # Create colored overlay
    overlay = np.zeros_like(img_array)
    
    # Color code the layers
    overlay[masks['foreground']] = [255, 100, 100]  # Red for foreground
    overlay[masks['middle']] = [100, 255, 100]      # Green for middle  
    overlay[masks['background']] = [100, 100, 255]  # Blue for background
    
    # Blend with original
    alpha = 0.4
    blended = (img_array * (1 - alpha) + overlay * alpha).astype(np.uint8)
    
    return Image.fromarray(blended)

def main():
    st.set_page_config(
        page_title="LayerText Pro - True Layer Insertion",
        page_icon="🎨", 
        layout="wide"
    )
    
    st.title("🎨 LayerText Pro - True Layer Insertion")
    st.markdown("*Insert text BETWEEN image layers - behind foreground, in front of background*")
    
    # Initialize session state
    if 'processor' not in st.session_state:
        st.session_state.processor = ImageLayerProcessor()
    if 'masks' not in st.session_state:
        st.session_state.masks = None
    if 'layers' not in st.session_state:
        st.session_state.layers = None
    if 'zones' not in st.session_state:
        st.session_state.zones = []
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 Controls")
        
        uploaded_file = st.file_uploader(
            "Choose an image...",
            type=['png', 'jpg', 'jpeg', 'webp']
        )
        
        if uploaded_file is not None:
            text_content = st.text_input("Text to insert", "SAMPLE TEXT")
            
            st.subheader("✨ Text Style")
            font_size = st.slider("Font Size", 20, 120, 60)
            text_color = st.color_picker("Text Color", "#FFFFFF")
            shadow_intensity = st.slider("Shadow Intensity", 0.0, 1.0, 0.8, 0.1)
            
            st.subheader("🔍 Layer Analysis")
            analysis_quality = st.selectbox("Analysis Quality", 
                                          ["Fast", "Balanced", "High Quality"],
                                          index=1)
            
            if st.button("🔄 Analyze Layers", type="primary"):
                with st.spinner("Analyzing image layers..."):
                    image = st.session_state.processor.load_image(uploaded_file)
                    
                    # Create depth map
                    depth_map = st.session_state.processor.create_advanced_depth_map(image)
                    
                    # Create layer masks
                    st.session_state.masks = st.session_state.processor.create_layer_masks(image, depth_map)
                    
                    # Extract layers
                    st.session_state.layers = st.session_state.processor.extract_layers(image, st.session_state.masks)
                    
                    # Find text zones
                    st.session_state.zones = st.session_state.processor.find_optimal_text_zones(
                        st.session_state.masks, image.size
                    )
                    
                st.success("✅ Layer analysis complete!")
    
    # Main content
    if uploaded_file is not None:
        image = st.session_state.processor.load_image(uploaded_file)
        
        tab1, tab2, tab3 = st.tabs(["🖼️ Original & Result", "🔍 Layer Analysis", "🎯 Text Placement"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📤 Original Image")
                st.image(image, use_column_width=True)
            
            with col2:
                st.subheader("✨ Result with Text Between Layers")
                
                if st.session_state.layers and st.session_state.zones and text_content:
                    # Get selected zone (default to best one)
                    if st.session_state.zones:
                        best_zone = st.session_state.zones[0]
                        
                        # Render text between layers
                        result = LayerTextRenderer.render_text_between_layers(
                            st.session_state.layers,
                            text_content,
                            (best_zone['x'], best_zone['y']),
                            font_size,
                            text_color,
                            shadow_intensity
                        )
                        
                        st.image(result, use_column_width=True)
                        
                        # Download button
                        buf = io.BytesIO()
                        result.save(buf, format='PNG', quality=95)
                        st.download_button(
                            label="📥 Download Result",
                            data=buf.getvalue(),
                            file_name=f"layered_text_{text_content.replace(' ', '_')[:10]}.png",
                            mime="image/png"
                        )
                else:
                    st.info("👆 Click 'Analyze Layers' to see the result!")
        
        with tab2:
            if st.session_state.masks is not None:
                st.subheader("🔍 Layer Breakdown")
                
                # Show layer visualization
                layer_viz = create_layer_visualization(st.session_state.masks, image)
                st.image(layer_viz, use_column_width=True, 
                        caption="Red=Foreground, Green=Middle (text zone), Blue=Background")
                
                # Show statistics
                col1, col2, col3 = st.columns(3)
                masks = st.session_state.masks
                total_pixels = masks['foreground'].size
                
                with col1:
                    fg_percent = np.sum(masks['foreground']) / total_pixels * 100
                    st.metric("🔴 Foreground", f"{fg_percent:.1f}%")
                
                with col2:
                    mid_percent = np.sum(masks['middle']) / total_pixels * 100
                    st.metric("🟢 Middle Layer", f"{mid_percent:.1f}%")
                
                with col3:
                    bg_percent = np.sum(masks['background']) / total_pixels * 100
                    st.metric("🔵 Background", f"{bg_percent:.1f}%")
                
                # Show extracted layers
                if st.session_state.layers:
                    st.subheader("📂 Extracted Layers")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Background Layer:**")
                        st.image(st.session_state.layers['background'], use_column_width=True)
                    
                    with col2:
                        st.write("**Foreground Layer:**")
                        st.image(st.session_state.layers['foreground'], use_column_width=True)
            else:
                st.info("Run layer analysis to see the breakdown.")
        
        with tab3:
            if st.session_state.zones:
                st.subheader("🎯 Available Text Zones")
                
                zone_names = [f"{zone['region']} (Score: {zone['score']:.2f})" for zone in st.session_state.zones]
                selected_zone_idx = st.selectbox("Choose text placement:", range(len(zone_names)),
                                                format_func=lambda x: zone_names[x])
                
                selected_zone = st.session_state.zones[selected_zone_idx]
                
                # Show zone details
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Zone Details:**")
                    st.write(f"- Quality Score: {selected_zone['score']:.2f}")
                    st.write(f"- Middle Layer Coverage: {selected_zone['coverage']*100:.1f}%") 
                    st.write(f"- Depth Level: {selected_zone['depth']:.2f}")
                
                with col2:
                    # Position adjustment
                    st.write("**Fine-tune Position:**")
                    x_offset = st.slider("X Offset", -100, 100, 0)
                    y_offset = st.slider("Y Offset", -50, 50, 0)
                
                # Generate preview with selected zone
                if text_content and st.session_state.layers:
                    final_pos = (selected_zone['x'] + x_offset, selected_zone['y'] + y_offset)
                    
                    preview_result = LayerTextRenderer.render_text_between_layers(
                        st.session_state.layers,
                        text_content,
                        final_pos,
                        font_size,
                        text_color,
                        shadow_intensity
                    )
                    
                    st.image(preview_result, use_column_width=True, caption="Preview with Selected Zone")
            else:
                st.info("Run layer analysis to see available text zones.")
    
    else:
        # Welcome screen
        st.markdown("""
        ## 🚀 True Layer-Based Text Insertion
        
        This application **actually separates your image into layers** and inserts text between them - not just on top!
        
        ### How it works:
        1. **🔍 Advanced Analysis**: Uses computer vision to separate foreground and background
        2. **✂️ Layer Extraction**: Actually cuts out the foreground objects  
        3. **📝 Smart Placement**: Places text in the middle layer space
        4. **🎭 Realistic Composition**: Foreground objects appear in front of your text
        
        ### Perfect Results For:
        - 👤 **Person in front of landscape** → Text behind person, in front of scenery
        - 🏠 **Buildings against sky** → Text behind buildings, in front of sky  
        - 🌳 **Objects in foreground** → Text appears naturally between layers
        - 📸 **Any image with clear depth** → Professional layered text effects
        
        ### ✨ Key Features:
        - **True layer separation** - not just overlay text
        - **Intelligent depth analysis** - finds the perfect spots
        - **Realistic shadows and effects** - matches the lighting
        - **Multiple placement zones** - choose the best position
        - **High-quality output** - professional results
        
        ---
        
        **Upload an image to experience true layer-based text insertion!** 
        
        *Works best with images that have clear foreground/background separation.*
        """)

if __name__ == "__main__":
    main()