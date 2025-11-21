# AI Text Behind Image - Documentation

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Getting Started](#getting-started)
4. [Application Versions](#application-versions)
5. [User Interface](#user-interface)
6. [Features](#features)
7. [AI Models](#ai-models)
8. [Text Effects](#text-effects)
9. [Advanced Settings](#advanced-settings)
10. [Command-Line Interface](#command-line-interface)
11. [Batch Processing](#batch-processing)
12. [Exporting](#exporting)
13. [Troubleshooting](#troubleshooting)
14. [API Reference](#api-reference)
15. [Performance Tips](#performance-tips)

## Introduction

AI Text Behind Image is a Python-based application that intelligently analyzes image depth layers and inserts custom text between foreground and background elements with realistic depth perception and lighting adaptation. The application uses state-of-the-art AI models for depth estimation and image segmentation to create visually appealing text insertions that appear to be part of the original scene.

### Key Features

- **Intelligent Image Segmentation**: Automatically detect and separate image layers (foreground, middle-ground, background)
- **Depth Analysis**: Determine optimal text placement zones between identified layers
- **Smart Text Rendering**: Render text with appropriate perspective, lighting, and shadows to match the scene
- **Real-time Preview**: Show users exactly how the text will appear before final rendering
- **Customization Options**: Font selection, size, color, opacity, and positioning controls
- **High-Quality Output**: Export processed images in multiple formats and resolutions

## Installation

### System Requirements

- Python 3.8 or higher
- 4GB RAM minimum (8GB or more recommended)
- 2GB free disk space for application and models
- CUDA-compatible GPU (optional, for faster processing)

### Windows Installation

1. Clone or download the repository
2. Open a command prompt in the project directory
3. Run the installation script:
   ```
   install.bat
   ```
4. Follow the on-screen instructions

### Linux/macOS Installation

1. Clone or download the repository
2. Open a terminal in the project directory
3. Make the installation script executable:
   ```
   chmod +x install.sh
   ```
4. Run the installation script:
   ```
   ./install.sh
   ```
5. Follow the on-screen instructions

### Manual Installation

1. Clone or download the repository
2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   ```
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/macOS: `source venv/bin/activate`
4. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
5. Download sample images (optional):
   ```
   python sample_images.py
   ```
6. Download AI models:
   ```
   python model_manager.py download --type depth --name Intel/dpt-large
   python model_manager.py download --type segmentation --name deeplabv3_resnet101
   ```

## Getting Started

### Running the Application

To start the application, run:

```
python start.py
```

This will launch the advanced version of the application. You can specify which version to run:

```
python start.py --app basic     # Basic version
python start.py --app advanced  # Advanced version
python start.py --app demo      # Demo version
```

### Quick Start Guide

1. Launch the application
2. Upload an image using the file uploader
3. Wait for the AI to analyze the image
4. Enter your text in the text input field
5. Customize the text appearance using the controls
6. Preview the result in real-time
7. Download the processed image

## Application Versions

### Basic Version (`app.py`)

The basic version provides essential functionality with a simplified interface:

- Depth estimation using a lightweight model
- Basic text rendering with limited effects
- Simple customization options
- Suitable for quick edits and lower-end hardware

### Advanced Version (`advanced_app.py`)

The advanced version offers full functionality with a comprehensive interface:

- High-quality depth estimation and segmentation
- Advanced text rendering with multiple effects
- Extensive customization options
- Real-time preview with depth map visualization
- Multiple export formats

### Demo Version (`demo.py`)

The demo version is designed to showcase the application's capabilities:

- Pre-loaded sample images
- Preset text and effects
- Step-by-step demonstration of features
- Comparison of different text effects

## User Interface

### Main Interface Components

- **Image Upload**: Upload your image for processing
- **Text Input**: Enter the text you want to insert
- **Text Customization**: Adjust font, size, color, and other properties
- **Depth Settings**: Control how text interacts with the image depth
- **Effect Controls**: Adjust perspective, shadow, and lighting effects
- **Preview**: See the processed image in real-time
- **Export Options**: Download the result in various formats

### Advanced Interface Features

- **Depth Map Visualization**: See the depth analysis of your image
- **Segmentation Mask**: View the segmentation of your image
- **Layer Controls**: Fine-tune the depth layers
- **Effect Presets**: Apply predefined combinations of effects
- **Batch Processing**: Process multiple images at once

## Features

### Depth Estimation

The application uses state-of-the-art depth estimation models to analyze the 3D structure of the image. This allows for realistic text placement that respects the scene's depth.

- **Model Options**: Choose between different depth estimation models
- **Depth Visualization**: See the depth map of your image
- **Depth Adjustment**: Fine-tune the depth analysis

### Image Segmentation

Image segmentation is used to identify different objects and regions in the image, allowing for more intelligent text placement.

- **Segmentation Models**: Choose between different segmentation models
- **Mask Visualization**: See the segmentation mask of your image
- **Object Detection**: Identify foreground and background objects

### Text Placement

The application automatically finds optimal regions for text placement based on depth analysis and segmentation.

- **Automatic Placement**: Let the AI find the best spot for your text
- **Manual Placement**: Drag and drop text to your preferred location
- **Depth-Aware Positioning**: Text respects the depth of the scene

### Text Rendering

Text is rendered with various effects to make it blend naturally with the scene.

- **Font Selection**: Choose from system fonts or load custom fonts
- **Size and Color**: Adjust text size and color
- **Opacity**: Control text transparency
- **Perspective**: Apply perspective transformation based on depth
- **Shadow**: Add realistic shadows that match the scene
- **Lighting Adaptation**: Adjust text brightness to match the scene lighting

## AI Models

### Depth Estimation Models

- **Intel/dpt-large**: High-quality depth estimation model
  - Pros: Very accurate depth maps
  - Cons: Slower processing, higher memory usage

- **Intel/dpt-hybrid-midas**: Faster depth estimation model
  - Pros: Good balance of speed and quality
  - Cons: Less detailed depth maps than dpt-large

### Segmentation Models

- **deeplabv3_resnet101**: High-quality segmentation model
  - Pros: Accurate segmentation with good object boundaries
  - Cons: Slower processing

- **fcn_resnet101**: Alternative segmentation model
  - Pros: Faster processing
  - Cons: Less detailed segmentation than deeplabv3

### Model Management

Use the model manager to download, update, and manage AI models:

```
python model_manager.py list  # List available models
python model_manager.py download --type depth --name Intel/dpt-large  # Download a model
python model_manager.py delete --type depth --name Intel/dpt-large  # Delete a model
```

## Text Effects

### Basic Effects

- **Color**: Change the text color
- **Opacity**: Adjust text transparency
- **Shadow**: Add a simple shadow effect
- **Glow**: Add a glow effect around the text

### Advanced Effects

- **Perspective Transformation**: Apply 3D perspective based on depth
- **Depth-Aware Shadow**: Cast shadows that respect scene depth
- **Lighting Adaptation**: Adjust text brightness based on scene lighting
- **3D Effect**: Create a 3D extrusion effect

### Effect Combinations

Combine multiple effects for more realistic results:

- **Natural Look**: Perspective + Shadow + Lighting Adaptation
- **Dramatic**: Strong Perspective + Dark Shadow + Glow
- **Subtle**: Mild Perspective + Light Shadow + High Opacity

## Advanced Settings

### Depth Settings

- **Depth Threshold**: Control which depth layers the text appears between
- **Depth Smoothing**: Adjust the smoothness of depth transitions
- **Layer Separation**: Control how distinctly layers are separated

### Rendering Settings

- **Rendering Quality**: Balance between quality and speed
- **Anti-aliasing**: Smooth text edges
- **Blending Mode**: How text blends with the background

### Performance Settings

- **Processing Resolution**: Adjust the resolution for processing
- **Preview Quality**: Control the quality of the real-time preview
- **GPU Acceleration**: Enable or disable GPU usage

## Command-Line Interface

The application provides a command-line interface for processing images without the web UI:

```
python cli.py --input image.jpg --output result.jpg --text "Hello World" --font "Arial" --size 60 --color "255,255,255" --opacity 0.8 --perspective 0.5 --shadow 0.7 --depth-threshold 0.5
```

### CLI Options

- `--input`: Input image path
- `--output`: Output image path
- `--text`: Text to insert
- `--font`: Font name or path
- `--size`: Font size
- `--color`: Text color (R,G,B)
- `--opacity`: Text opacity (0.0-1.0)
- `--perspective`: Perspective strength (0.0-1.0)
- `--shadow`: Shadow strength (0.0-1.0)
- `--depth-threshold`: Depth threshold (0.0-1.0)
- `--show-depth`: Save depth map visualization

## Batch Processing

Process multiple images at once using the batch processor:

```
python batch_processor.py --input-dir images/ --output-dir results/ --text "Hello World" --font "Arial" --size 60 --color "255,255,255" --opacity 0.8 --perspective 0.5 --shadow 0.7 --depth-threshold 0.5
```

### Batch Processing Options

- `--input-dir`: Input directory containing images
- `--output-dir`: Output directory for processed images
- `--text`: Text to insert (can include {filename} placeholder)
- `--font`: Font name or path
- `--size`: Font size
- `--color`: Text color (R,G,B)
- `--opacity`: Text opacity (0.0-1.0)
- `--perspective`: Perspective strength (0.0-1.0)
- `--shadow`: Shadow strength (0.0-1.0)
- `--depth-threshold`: Depth threshold (0.0-1.0)
- `--recursive`: Process subdirectories recursively

## Exporting

### Export Formats

- **PNG**: Lossless compression with transparency support
- **JPEG**: Lossy compression with smaller file size
- **WEBP**: Modern format with good compression and quality
- **TIFF**: High-quality format for professional use

### Export Options

- **Quality**: Adjust compression quality (for JPEG and WEBP)
- **Resolution**: Export at different resolutions
- **DPI**: Set the dots per inch for printing
- **Metadata**: Include processing information in metadata

### Export Utilities

Use the export utilities to convert between formats and adjust export settings:

```
python export_utils.py --image result.jpg --output result.png --format PNG --quality 95 --dpi 300
```

## Troubleshooting

### Common Issues

#### Installation Problems

- **Missing Dependencies**: Make sure all required packages are installed
- **CUDA Issues**: Check CUDA compatibility with PyTorch
- **Memory Errors**: Reduce model size or processing resolution

#### Processing Issues

- **Poor Depth Estimation**: Try a different depth model or adjust depth settings
- **Text Placement Problems**: Adjust depth threshold or try manual placement
- **Slow Processing**: Enable GPU acceleration or use lighter models

### Error Messages

- **"Model not found"**: Download the required model using the model manager
- **"CUDA out of memory"**: Reduce processing resolution or use CPU mode
- **"Invalid image format"**: Ensure the image is in a supported format

## API Reference

### Main Modules

- **ai_models.py**: AI model handling and prediction
- **image_utils.py**: Image processing utilities
- **text_renderer.py**: Text rendering and effects
- **export_utils.py**: Export and format conversion

### Key Classes

#### ModelFactory

```python
from ai_models import ModelFactory

# Create a model factory
model_factory = ModelFactory()

# Get a depth estimation model
depth_model = model_factory.get_model("depth", model_name="Intel/dpt-large")

# Get a segmentation model
segmentation_model = model_factory.get_model("segmentation", model_name="deeplabv3_resnet101")
```

#### TextRenderer

```python
from text_renderer import TextRenderer
from PIL import ImageFont, Image

# Create a text renderer
font = ImageFont.truetype("arial.ttf", 60)
renderer = TextRenderer(font=font)

# Render text on an image
image = Image.open("image.jpg")
renderer.render_text(image, "Hello World", (100, 100), color=(255, 255, 255), shadow=True)
```

#### AdvancedTextRenderer

```python
from text_renderer import AdvancedTextRenderer
from PIL import ImageFont, Image
import numpy as np

# Create an advanced text renderer
font = ImageFont.truetype("arial.ttf", 60)
renderer = AdvancedTextRenderer(font=font)

# Render text with depth awareness
image = Image.open("image.jpg")
depth_map = np.load("depth_map.npy")
renderer.render_text_with_depth(
    image, "Hello World", (100, 100), depth_map,
    color=(255, 255, 255),
    perspective_strength=0.5,
    shadow=True,
    shadow_strength=0.7,
    adapt_lighting=True
)
```

## Performance Tips

### Hardware Recommendations

- **CPU**: Multi-core processor (4+ cores recommended)
- **RAM**: 8GB minimum, 16GB recommended
- **GPU**: NVIDIA GPU with CUDA support for faster processing
- **Storage**: SSD for faster model loading and image processing

### Optimization Strategies

- **Use Appropriate Models**: Choose lighter models for faster processing
- **Reduce Processing Resolution**: Process at lower resolution for speed
- **Batch Processing**: Process multiple images at once for efficiency
- **Pre-download Models**: Download models in advance to avoid delays

### Memory Management

- **Clear Cache**: Use the model manager to clear unused models
- **Limit Concurrent Processing**: Process one image at a time on low-memory systems
- **Close Other Applications**: Free up system resources during processing