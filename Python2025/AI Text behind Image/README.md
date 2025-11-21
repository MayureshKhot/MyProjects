# AI Text Behind Image

A Python-based SaaS application that intelligently analyzes image depth layers and inserts custom text between foreground and background elements with realistic depth perception and lighting adaptation.

## Features

- **Intelligent Image Segmentation**: Uses AI/ML models to automatically detect and separate image layers (foreground, middle-ground, background)
- **Depth Analysis**: Determines optimal text placement zones between identified layers
- **Smart Text Rendering**: Renders text with appropriate perspective, lighting, and shadows to match the scene
- **Real-time Preview**: Shows users exactly how the text will appear before final rendering
- **Customization Options**: Font selection, size, color, opacity, and positioning controls
- **High-Quality Output**: Exports processed images in multiple formats and resolutions

## Installation

### Standard Installation

1. Clone this repository:
   ```
   git clone https://github.com/mayureshkhot/ai-text-behind-image.git
   cd ai-text-behind-image
   ```

2. Check if your system meets the requirements:
   ```
   # Windows
   python check_system.py
   
   # Linux/macOS
   python3 check_system.py
   ```

3. Install the required dependencies:

   #### Option 1: Direct Installation
   ```
   # Windows
   pip install -r requirements.txt
   
   # Linux/macOS
   pip3 install -r requirements.txt
   ```

   #### Option 2: Using Virtual Environment (Recommended)
   ```
   # Create and set up a virtual environment
   python create_venv.py
   
   # Activate the virtual environment
   # Windows
   activate_venv.bat
   
   # Linux/macOS
   source activate_venv.sh
   ```

4. (Optional) Download sample images and AI models:
   ```
   # Windows
   python ai_text_behind_image.py samples
   python ai_text_behind_image.py models
   
   # Linux/macOS
   python3 ai_text_behind_image.py samples
   python3 ai_text_behind_image.py models
   ```

5. (Optional) Set up API keys for enhanced analysis:
   - Create a `.env` file in the project root
   - Add your API keys:
     ```
     GEMINI_API_KEY=your_gemini_api_key
     OPENAI_API_KEY=your_openai_api_key
     ```

### Docker Installation

Alternatively, you can run the application in a Docker container:

1. Make sure you have Docker and Docker Compose installed on your system.

2. Clone the repository:
   ```
   git clone https://github.com/mayureshkhot/ai-text-behind-image.git
   cd ai-text-behind-image
   ```

3. Build and start the Docker container:
   ```
   docker-compose up -d
   ```

4. Access the application at http://localhost:8501

5. To stop the container:
   ```
   docker-compose down
   ```

## Usage

### Quick Start

The easiest way to get started is to use the `get_started.py` script, which will set up everything for you:

```
# Windows
python get_started.py

# Linux/macOS
python3 get_started.py
```

This script will:
1. Check your environment and install required dependencies
2. Download sample images for testing
3. Download required AI models
4. Run a quick test to verify everything is working
5. Start the application

You can also quickly test the application with a sample image:

```
# Windows
python quick_test.py

# Linux/macOS
python3 quick_test.py
```

This will download a sample image and required AI models if needed, process the image with default text, and display the result.

### Using the Unified Interface

The application provides a unified command-line interface for all operations:

```
python ai_text_behind_image.py [command] [options]
```

Available commands:

- **run**: Start the application (basic, advanced, or demo version)
- **samples**: Download sample images for testing
- **models**: Download required AI models
- **examples**: Run example scripts
- **benchmark**: Run performance benchmarks
- **batch**: Process multiple images in batch mode
- **cli**: Use the command-line interface for single image processing
- **fonts**: Create a catalog of available fonts

Examples:

```
# Run the advanced application
python ai_text_behind_image.py run --app advanced

# Run the basic application on a specific port
python ai_text_behind_image.py run --app basic --port 8502

# Process a single image via CLI
python ai_text_behind_image.py cli --input input.jpg --output output.jpg --text "Hello World"

# Process multiple images in batch mode
python ai_text_behind_image.py batch --input-dir images/ --output-dir results/ --text "Hello World"
```

### Alternative Methods

You can also run the applications directly:

```
# Basic application
streamlit run app.py

# Advanced application
streamlit run advanced_app.py

# Demo application
streamlit run demo.py
```

### Maintenance

The application includes several maintenance scripts:

```
# Check if your system meets the requirements
python check_system.py

# Clean up temporary files and cached data
python cleanup.py

# Update the application to the latest version
python update.py

# Check for updates without installing them
python update.py --check

# Generate a comprehensive system report
python generate_report.py

# Generate a report in JSON format
python generate_report.py --format json

# Run all tests to verify the application is working correctly
python run_tests.py

# Run specific tests with verbose output
python run_tests.py --component --model --verbose
```

#### Uninstallation
To uninstall the application and remove its components:
```
python uninstall.py
```

Options:
- `--all`: Remove everything (packages, models, samples, output, cache)
- `--packages`: Uninstall Python packages
- `--models`: Remove model cache
- `--samples`: Remove sample images
- `--output`: Remove output files
- `--cache`: Remove cache files
- `--yes`: Skip confirmation

Examples:
```
# Uninstall everything without confirmation
python uninstall.py --all --yes

# Only remove sample images and output files
python uninstall.py --samples --output

# Only uninstall Python packages
python uninstall.py --packages
```

### User Workflow

1. **Upload Image**: Select an image file (PNG, JPG, WEBP)
2. **AI Analysis**: The application automatically analyzes the image layers and depth
3. **Enter Text**: Type the text you want to insert
4. **Preview Placement**: See real-time preview of text placement
5. **Customize Appearance**: Adjust font, size, color, opacity, and effects
6. **Download Result**: Export the final image in your preferred format

## Technical Details

### Components

### Core Components
- **ai_text_behind_image.py**: Unified command-line interface for all operations
- **app.py**: Basic Streamlit web interface
- **advanced_app.py**: Enhanced version with additional features
- **demo.py**: Demonstration application with sample images
- **image_utils.py**: Utility functions for image processing
- **ai_models.py**: AI model integrations for depth estimation and segmentation
- **text_renderer.py**: Advanced text rendering with effects

### Utility Scripts
- **get_started.py**: Set up everything and start the application
- **create_venv.py**: Create and set up a virtual environment
- **cli.py**: Command-line interface for processing single images
- **batch_processor.py**: Batch processing for multiple images
- **benchmark.py**: Performance benchmarking for AI models
- **examples.py**: Example scripts demonstrating various features
- **model_manager.py**: Tool for managing AI models
- **font_utils.py**: Utilities for font management and preview
- **export_utils.py**: Functions for exporting images in various formats
- **quick_test.py**: Quick test with a sample image
- **check_system.py**: Check if your system meets the requirements
- **cleanup.py**: Clean up temporary files and cached data
- **update.py**: Update the application to the latest version
- **generate_report.py**: Generate a comprehensive system report
- **run_tests.py**: Run tests to verify the application is working correctly
- **uninstall.py**: Uninstall the application and its components

### Docker Files
- **Dockerfile**: Configuration for building a Docker image
- **docker-compose.yml**: Configuration for running the application with Docker Compose

### AI Models Used

- **Depth Estimation**: Intel/dpt-large model for accurate depth map generation
- **Image Segmentation**: DeepLabV3 with ResNet-101 backbone for layer separation
- **External APIs**: Optional integration with Gemini/OpenAI for enhanced analysis

## Customization

### Text Effects

The application supports various text effects:

- **Perspective**: Adds 3D perspective to match the scene
- **Shadows**: Realistic shadows based on depth information
- **Lighting Adaptation**: Adjusts text brightness to match the scene lighting
- **3D Effect**: Creates a 3D extrusion effect
- **Glow**: Adds a subtle glow around the text

### Advanced Settings

In the advanced application, you can also adjust:

- **Depth Threshold**: Controls where in the depth range text is placed
- **Shadow Strength**: Adjusts the intensity of shadows
- **Perspective Amount**: Controls the strength of perspective effect

## Requirements

- Python 3.8+
- Streamlit
- PyTorch
- OpenCV
- PIL (Pillow)
- Transformers
- NumPy
- scikit-image
- Matplotlib

## License

MIT

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines on how to contribute to this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.