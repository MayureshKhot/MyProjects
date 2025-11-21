import os
import sys
import numpy as np
from PIL import Image
import torch
import cv2
import matplotlib.pyplot as plt

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our modules
from ai_models import ModelFactory
from text_renderer import TextRenderer, AdvancedTextRenderer
from image_utils import visualize_depth_map, create_depth_layers, find_optimal_text_regions

def test_models():
    """Test that AI models can be loaded and run."""
    print("Testing AI models...")
    
    # Check if CUDA is available
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"CUDA device: {torch.cuda.get_device_name(0)}")
    
    try:
        # Try to load the depth model
        print("Loading depth estimation model...")
        depth_model = ModelFactory.get_depth_model()
        print("✓ Depth model loaded successfully")
        
        # Try to load the segmentation model
        print("Loading segmentation model...")
        segmentation_model = ModelFactory.get_segmentation_model()
        print("✓ Segmentation model loaded successfully")
        
        return True
    except Exception as e:
        print(f"Error loading models: {e}")
        return False

def test_text_renderer():
    """Test the text rendering functionality."""
    print("\nTesting text renderer...")
    
    try:
        # Create a simple test image
        image = Image.new('RGB', (800, 600), color=(73, 109, 137))
        
        # Create a text renderer
        renderer = TextRenderer()
        
        # Test basic text rendering
        print("Testing basic text rendering...")
        placement_zone = (200, 200, 600, 400)
        result = renderer.render_text(
            image, "Test Text", placement_zone, 
            font_size=40, color=(255, 255, 255), opacity=0.9
        )
        
        # Check that result is a PIL Image
        if isinstance(result, Image.Image):
            print("✓ Basic text rendering successful")
        else:
            print("✗ Basic text rendering failed")
            return False
        
        # Test advanced text rendering
        print("Testing advanced text rendering...")
        advanced_renderer = AdvancedTextRenderer()
        
        # Create a simple depth map for testing
        depth_map = np.ones((600, 800)) * 0.5
        # Add some variation to the depth map
        depth_map[150:450, 150:650] = 0.7
        
        # Test depth-aware text rendering
        result = advanced_renderer.render_text_with_depth(
            image, "Depth Test", depth_map,
            font_size=40, color=(255, 255, 255), opacity=0.9,
            effects={'perspective': 0.2, 'shadow': True, 'lighting_adaptation': True}
        )
        
        # Check that result is a PIL Image
        if isinstance(result, Image.Image):
            print("✓ Advanced text rendering successful")
            return True
        else:
            print("✗ Advanced text rendering failed")
            return False
            
    except Exception as e:
        print(f"Error testing text renderer: {e}")
        return False

def test_image_utils():
    """Test the image utility functions."""
    print("\nTesting image utilities...")
    
    try:
        # Create a simple test depth map
        depth_map = np.zeros((600, 800))
        # Add some variation to the depth map
        depth_map[0:200, :] = 0.2  # Foreground
        depth_map[200:400, :] = 0.5  # Midground
        depth_map[400:600, :] = 0.8  # Background
        
        # Test depth map visualization
        print("Testing depth map visualization...")
        vis_result = visualize_depth_map(depth_map)
        if isinstance(vis_result, np.ndarray) and vis_result.shape[2] == 3:
            print("✓ Depth map visualization successful")
        else:
            print("✗ Depth map visualization failed")
            return False
        
        # Test depth layer creation
        print("Testing depth layer creation...")
        layers = create_depth_layers(depth_map, num_layers=3)
        if isinstance(layers, list) and len(layers) == 3:
            print("✓ Depth layer creation successful")
        else:
            print("✗ Depth layer creation failed")
            return False
        
        # Test optimal text region finding
        print("Testing optimal text region finding...")
        image = Image.new('RGB', (800, 600), color=(73, 109, 137))
        regions = find_optimal_text_regions(image, depth_map)
        if isinstance(regions, list):
            print("✓ Optimal text region finding successful")
            return True
        else:
            print("✗ Optimal text region finding failed")
            return False
            
    except Exception as e:
        print(f"Error testing image utilities: {e}")
        return False

def run_all_tests():
    """Run all component tests."""
    print("Running component tests for AI Text Behind Image\n" + "-" * 50)
    
    # Test models
    models_ok = test_models()
    
    # Test text renderer
    renderer_ok = test_text_renderer()
    
    # Test image utilities
    utils_ok = test_image_utils()
    
    # Print summary
    print("\n" + "-" * 50)
    print("Test Summary:")
    print(f"AI Models: {'✓ PASSED' if models_ok else '✗ FAILED'}")
    print(f"Text Renderer: {'✓ PASSED' if renderer_ok else '✗ FAILED'}")
    print(f"Image Utilities: {'✓ PASSED' if utils_ok else '✗ FAILED'}")
    
    if models_ok and renderer_ok and utils_ok:
        print("\nAll tests passed! The application should work correctly.")
        return True
    else:
        print("\nSome tests failed. Please check the error messages above.")
        return False

if __name__ == "__main__":
    run_all_tests()