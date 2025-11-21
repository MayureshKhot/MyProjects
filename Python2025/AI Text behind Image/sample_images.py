import os
import sys
import requests
from PIL import Image
import io
import argparse

def download_sample_images(output_dir="sample_images", num_images=5):
    """Download sample images for testing the application."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Sample image URLs with good depth characteristics
    sample_urls = [
        # Landscape with clear foreground/background separation
        "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80",
        
        # Portrait with person in foreground
        "https://images.unsplash.com/photo-1544005313-94ddf0286df2?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80",
        
        # City street with buildings
        "https://images.unsplash.com/photo-1514924013411-cbf25faa35bb?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80",
        
        # Nature scene with trees
        "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80",
        
        # Beach scene
        "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80",
        
        # Urban scene with depth
        "https://images.unsplash.com/photo-1449824913935-59a10b8d2000?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80",
        
        # Indoor scene with depth
        "https://images.unsplash.com/photo-1493809842364-78817add7ffb?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80",
        
        # Product with clear background
        "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80",
        
        # Architecture with depth
        "https://images.unsplash.com/photo-1487958449943-2429e8be8625?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80",
        
        # Food photography with depth
        "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80"
    ]
    
    # Limit to requested number of images
    sample_urls = sample_urls[:num_images]
    
    # Download each image
    downloaded_paths = []
    for i, url in enumerate(sample_urls):
        try:
            print(f"Downloading image {i+1}/{len(sample_urls)}...")
            response = requests.get(url)
            image = Image.open(io.BytesIO(response.content))
            
            # Create filename
            filename = f"sample_{i+1}.jpg"
            filepath = os.path.join(output_dir, filename)
            
            # Save image
            image.save(filepath, "JPEG")
            downloaded_paths.append(filepath)
            
            print(f"  Saved to {filepath}")
        
        except Exception as e:
            print(f"  Error downloading image {i+1}: {e}")
    
    print(f"\nDownloaded {len(downloaded_paths)} sample images to {output_dir}/")
    return downloaded_paths

def main():
    parser = argparse.ArgumentParser(description="Download sample images for testing")
    
    parser.add_argument("--output", default="sample_images", help="Output directory for sample images")
    parser.add_argument("--count", type=int, default=5, help="Number of sample images to download (max 10)")
    
    args = parser.parse_args()
    
    # Limit count to available images
    count = min(args.count, 10)
    
    # Download images
    download_sample_images(args.output, count)

if __name__ == "__main__":
    main()