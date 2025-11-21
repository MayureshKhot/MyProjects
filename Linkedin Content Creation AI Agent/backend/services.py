import os
from groq import Groq
from tavily import TavilyClient
import base64
from io import BytesIO
from typing import Optional, Dict, Any
from fastapi import HTTPException

# Initialize API clients as None
groq_client = None
tavily_client = None

def get_groq_client():
    """Get or initialize the Groq client."""
    global groq_client
    if groq_client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=500,
                detail="GROQ_API_KEY environment variable is not set"
            )
        groq_client = Groq(api_key=api_key)
    return groq_client

def get_tavily_client():
    """Get or initialize the Tavily client."""
    global tavily_client
    if tavily_client is None:
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=500,
                detail="TAVILY_API_KEY environment variable is not set"
            )
        tavily_client = TavilyClient(api_key=api_key)
    return tavily_client

PROMPT_TEMPLATES = {
    "hormozi_insights": {
        "id": "hormozi_insights",
        "name": "Hormozi-Style Business Lessons",
        "description": "Share business insights in Alex Hormozi's direct, value-focused style",
        "template": "Here are {number} key lessons about {topic} that will help you scale your {business_type}:"
    },
    "naval_wisdom": {
        "id": "naval_wisdom",
        "name": "Naval-Style Wisdom",
        "description": "Share philosophical insights in Naval's clear, principle-based approach",
        "template": "{topic} - A Different Perspective\n\nHere's what most people miss about {subject}:"
    },
    "mrbeast_challenge": {
        "id": "mrbeast_challenge",
        "name": "MrBeast-Style Challenge",
        "description": "Share ambitious goals and challenges in MrBeast's engaging style",
        "template": "I challenged myself to {challenge} in {timeframe}. Here's what happened:"
    },
    "erwin_leadership": {
        "id": "erwin_leadership",
        "name": "Erwin-Style Leadership",
        "description": "Share leadership insights with Commander Erwin's strategic vision",
        "template": "Leadership lesson from the frontlines: {situation} taught me this about {topic}."
    },
    "job_update": {
        "id": "job_update",
        "name": "Job Update",
        "description": "Announce career changes or achievements",
        "template": "Excited to share that {announcement}. {additional_details}"
    },
    "networking": {
        "id": "networking",
        "name": "Networking",
        "description": "Connect with professionals",
        "template": "Looking to connect with {professional_type} in {industry} to discuss {topic}."
    }
}

TONE_MODIFIERS = {
    "hormozi": "Write this in Alex Hormozi's style: direct, actionable insights, numbered points, focus on business value and ROI. Use simple language but maintain the hard-hitting business truth approach.",
    
    "naval": "Write this in Naval Ravikant's style: philosophical, clear principles, focus on wealth creation and personal growth. Break down complex ideas into simple, memorable insights.",
    
    "mrbeast": "Write this in MrBeast's style: high-energy, engaging, focus on ambitious goals and challenges. Make it exciting while keeping it professional and inspiring.",
    
    "erwin": "Write this in Commander Erwin Smith's style: strategic, inspiring, focused on long-term vision and leadership. Balance between determination and wisdom.",
    
    "levi": "Write this in Levi Ackerman's style: direct, efficient, no unnecessary words. Focus on practical execution and getting results.",
    
    "itachi": "Write this in Itachi Uchiha's style: wise, thoughtful, focused on long-term impact. Balance between personal growth and collective benefit.",
    
    "professional": "Write this in a formal and professional tone, focusing on business value and expertise.",
    "friendly": "Write this in a warm and approachable tone, while maintaining professional standards.",
    "inspirational": "Write this in an inspiring and motivational tone that encourages and uplifts.",
    "confident": "Write this in a confident and authoritative tone that demonstrates leadership."
}

async def generate_text(prompt: str, tone_style: Optional[str] = None, operation: str = "generate") -> str:
    try:
        client = get_groq_client()
        
        # Base system prompt
        system_prompt = """You are a professional LinkedIn content creator. 
        Create engaging, professional LinkedIn posts that are informative, valuable and shareable. 
        Include relevant hashtags and maintain a professional tone.
        Format the post with proper paragraphs and line breaks.
        Keep the post concise but impactful and insightful."""
        
        # Add tone modifier if specified
        if tone_style and tone_style in TONE_MODIFIERS:
            system_prompt += f"\n{TONE_MODIFIERS[tone_style]}"
        
        # Modify prompt based on operation
        user_prompt = prompt
        if operation == "summarize":
            user_prompt = f"Please summarize the following LinkedIn post while maintaining its key message and impact:\n\n{prompt}"
        elif operation == "expand":
            user_prompt = f"Please expand the following brief LinkedIn post into a more detailed and engaging version:\n\n{prompt}"
        elif operation == "improve":
            user_prompt = f"Please improve the following LinkedIn post for better clarity, engagement, and impact while maintaining its core message:\n\n{prompt}"
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=1000,
            top_p=0.9,
            frequency_penalty=0.1
        )
        
        if not completion.choices or not completion.choices[0].message.content:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate text: Empty response from API"
            )
            
        return completion.choices[0].message.content
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating text: {str(e)}"
        )

# Add new endpoint to get templates
# Add after TONE_MODIFIERS dictionary
USER_TEMPLATES = {}
USER_TONES = {}

# Add new functions for managing custom templates and tones
# Add validation for template/tone data
async def add_custom_template(template_data: Dict[str, Any]) -> Dict[str, Any]:
    if not template_data.get("name") or not template_data.get("template"):
        raise HTTPException(
            status_code=400,
            detail="Name and template are required fields"
        )
    template_id = f"custom_{len(USER_TEMPLATES)}"
    USER_TEMPLATES[template_id] = {
        "id": template_id,
        "name": template_data["name"],
        "description": template_data.get("description", ""),
        "template": template_data["template"],
        "isCustom": True
    }
    return USER_TEMPLATES[template_id]

async def add_custom_tone(tone_data: Dict[str, Any]) -> Dict[str, Any]:
    tone_id = f"custom_{len(USER_TONES)}"
    USER_TONES[tone_id] = {
        "id": tone_id,
        "name": tone_data["name"],
        "description": tone_data["description"],
        "modifier": tone_data["modifier"],
        "isCustom": True
    }
    return USER_TONES[tone_id]

# Modify get_prompt_templates to include custom templates
async def get_prompt_templates() -> Dict:
    return {**PROMPT_TEMPLATES, **USER_TEMPLATES}

# Add function to get all tones
async def get_tone_styles() -> Dict:
    return {**TONE_MODIFIERS, **USER_TONES}

async def generate_image(prompt: str) -> str:
    """
    Generate an image using Groq API.
    Note: Currently using a placeholder as Groq doesn't support image generation.
    
    Args:
        prompt (str): Text prompt for image generation
        
    Returns:
        str: URL of the generated image
        
    Raises:
        HTTPException: If image generation fails
    """
    try:
        # TODO: Replace with actual image generation service
        # Options: DALL-E, Stable Diffusion, or other image generation APIs
        return "https://via.placeholder.com/800x600?text=AI+Generated+Image"
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating image: {str(e)}"
        )

async def search_web(query: str) -> list:
    """
    Perform web search using Tavily API.
    
    Args:
        query (str): Search query
        
    Returns:
        list: List of search results
        
    Raises:
        HTTPException: If search fails or returns invalid response
    """
    try:
        client = get_tavily_client()
        search_result = client.search(
            query=query,
            search_depth="advanced",
            include_answer=True,
            include_domains=[],
            exclude_domains=[],
            max_results=5
        )
        
        if not isinstance(search_result, dict) or "results" not in search_result:
            raise HTTPException(
                status_code=500,
                detail="Invalid response format from Tavily API"
            )
            
        return search_result.get("results", [])
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error performing web search: {str(e)}"
        )