from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import os
from dotenv import load_dotenv
from services import generate_text, generate_image, search_web, get_prompt_templates

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="LinkedIn Content Generator API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str

class GenerateResponse(BaseModel):
    text: str
    image_url: Optional[str] = None
    web_search_results: Optional[List[SearchResult]] = None

class GenerateRequest(BaseModel):
    prompt: str
    web_search: bool = False
    image_prompt: Optional[str] = None
    tone_style: Optional[str] = None
    operation: str = "generate"
    template_id: Optional[str] = None

@app.post("/generate", response_model=GenerateResponse)
async def generate_content(request: GenerateRequest):
    try:
        # Generate text content
        text = await generate_text(request.prompt, request.tone_style, request.operation)
        
        # Generate image if prompt is provided
        image_url = None
        if request.image_prompt:
            image_url = await generate_image(request.image_prompt)
        
        # Perform web search if enabled
        web_search_results = None
        if request.web_search:
            web_search_results = await search_web(request.prompt)
        
        return GenerateResponse(
            text=text,
            image_url=image_url,
            web_search_results=web_search_results
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/templates", response_model=Dict)
async def get_available_templates():
    """Get all available prompt templates"""
    try:
        templates = await get_prompt_templates()
        return templates
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching templates: {str(e)}"
        )