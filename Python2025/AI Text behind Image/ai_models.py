import torch
import numpy as np
from transformers import pipeline, AutoImageProcessor, AutoModelForDepthEstimation
from torchvision import models, transforms
from PIL import Image
import os
import requests
from dotenv import load_dotenv

# Load environment variables for API keys
load_dotenv()

# Base class for AI models
class BaseModel:
    def __init__(self):
        self.model = None
        self.processor = None
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    def load(self):
        """Load the model. To be implemented by subclasses."""
        raise NotImplementedError
    
    def predict(self, image):
        """Make a prediction. To be implemented by subclasses."""
        raise NotImplementedError

# Depth Estimation Model
class DepthEstimationModel(BaseModel):
    def __init__(self, model_name="Intel/dpt-large"):
        super().__init__()
        self.model_name = model_name
    
    def load(self):
        """Load the depth estimation model."""
        self.processor = AutoImageProcessor.from_pretrained(self.model_name)
        self.model = AutoModelForDepthEstimation.from_pretrained(self.model_name).to(self.device)
        return self
    
    def predict(self, image):
        """Predict depth map from image."""
        # Convert PIL Image to numpy array if needed
        if isinstance(image, Image.Image):
            image_np = np.array(image)
        else:
            image_np = image
        
        # Prepare image for the model
        inputs = self.processor(images=image_np, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            predicted_depth = outputs.predicted_depth
        
        # Interpolate to original size
        prediction = torch.nn.functional.interpolate(
            predicted_depth.unsqueeze(1),
            size=image_np.shape[:2],
            mode="bicubic",
            align_corners=False,
        ).squeeze()
        
        depth_map = prediction.cpu().numpy()
        return depth_map

# Image Segmentation Model
class SegmentationModel(BaseModel):
    def __init__(self, model_name="deeplabv3_resnet101"):
        super().__init__()
        self.model_name = model_name
    
    def load(self):
        """Load the segmentation model."""
        if self.model_name == "deeplabv3_resnet101":
            from torchvision.models.segmentation import DeepLabV3_ResNet101_Weights
            weights = DeepLabV3_ResNet101_Weights.DEFAULT
            self.model = models.segmentation.deeplabv3_resnet101(weights=weights).to(self.device)
        elif self.model_name == "fcn_resnet101":
            from torchvision.models.segmentation import FCN_ResNet101_Weights
            weights = FCN_ResNet101_Weights.DEFAULT
            self.model = models.segmentation.fcn_resnet101(weights=weights).to(self.device)
        else:
            raise ValueError(f"Unsupported segmentation model: {self.model_name}")
        
        self.model.eval()
        
        # Define preprocessing
        self.preprocess = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        
        return self
    
    def predict(self, image):
        """Predict segmentation mask from image."""
        # Convert PIL Image to tensor
        if isinstance(image, Image.Image):
            input_tensor = self.preprocess(image)
        else:
            input_tensor = self.preprocess(Image.fromarray(image))
        
        input_batch = input_tensor.unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            output = self.model(input_batch)['out'][0]
        
        output_predictions = output.argmax(0).byte().cpu().numpy()
        
        return output_predictions

# External API Integration for Enhanced Analysis
class ExternalAIAPI:
    def __init__(self, api_type="gemini"):
        self.api_type = api_type
        self.api_key = self._get_api_key()
    
    def _get_api_key(self):
        """Get API key from environment variables."""
        if self.api_type == "gemini":
            return os.getenv("GEMINI_API_KEY")
        elif self.api_type == "openai":
            return os.getenv("OPENAI_API_KEY")
        else:
            raise ValueError(f"Unsupported API type: {self.api_type}")
    
    def analyze_image(self, image, prompt):
        """Analyze image using external AI API."""
        if self.api_type == "gemini":
            return self._analyze_with_gemini(image, prompt)
        elif self.api_type == "openai":
            return self._analyze_with_openai(image, prompt)
    
    def _analyze_with_gemini(self, image, prompt):
        """Analyze image using Google's Gemini API."""
        if not self.api_key:
            return {"error": "Gemini API key not found. Please set GEMINI_API_KEY environment variable."}
        
        # Convert image to base64 if it's a PIL Image
        if isinstance(image, Image.Image):
            import base64
            from io import BytesIO
            buffered = BytesIO()
            image.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        else:
            return {"error": "Image must be a PIL Image."}
        
        # Gemini API endpoint
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-vision:generateContent"
        
        # Prepare request payload
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": img_str
                            }
                        }
                    ]
                }
            ]
        }
        
        # Make API request
        response = requests.post(
            f"{url}?key={self.api_key}",
            json=payload
        )
        
        return response.json()
    
    def _analyze_with_openai(self, image, prompt):
        """Analyze image using OpenAI's API."""
        if not self.api_key:
            return {"error": "OpenAI API key not found. Please set OPENAI_API_KEY environment variable."}
        
        # Convert image to base64 if it's a PIL Image
        if isinstance(image, Image.Image):
            import base64
            from io import BytesIO
            buffered = BytesIO()
            image.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        else:
            return {"error": "Image must be a PIL Image."}
        
        # OpenAI API endpoint
        url = "https://api.openai.com/v1/chat/completions"
        
        # Prepare request payload
        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{img_str}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 300
        }
        
        # Make API request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        return response.json()

# Model Factory
class ModelFactory:
    @staticmethod
    def get_depth_model(model_name="Intel/dpt-large"):
        """Get a depth estimation model."""
        return DepthEstimationModel(model_name).load()
    
    @staticmethod
    def get_segmentation_model(model_name="deeplabv3_resnet101"):
        """Get a segmentation model."""
        return SegmentationModel(model_name).load()
    
    @staticmethod
    def get_external_api(api_type="gemini"):
        """Get an external API integration."""
        return ExternalAIAPI(api_type)