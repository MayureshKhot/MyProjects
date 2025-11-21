import os
import uvicorn  # ASGI server
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from groq import Groq, GroqError
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    print("Warning: GROQ_API_KEY environment variable not set. Using mock response.")
   
CLIENT_NAME = "Akhand Solutions"
CLIENT_LOCATION = "Pune, India"
CLIENT_SERVICES = [
    "Custom Website Development (using technologies like Python/Django, Node.js/React, PHP/WordPress)",
    "E-commerce Website Development",
    "Website Maintenance and Support",
    "Search Engine Optimization (SEO)",
    "Social Media Marketing (SMM)",
    "Pay-Per-Click (PPC) Advertising Management",
    "Content Marketing",
]

SYSTEM_PROMPT = f"""
You are a helpful and concise AI assistant representing {CLIENT_NAME}, a company based in {CLIENT_LOCATION}.
Your goal is to answer questions from potential website visitors about {CLIENT_NAME}'s services.

**Your Knowledge Base:**
- Company Name: {CLIENT_NAME}
- Location: {CLIENT_LOCATION}
- Core Services: {', '.join(CLIENT_SERVICES)}.

**Your Instructions:**
1.  **Be Polite and Professional:** Always maintain a helpful and professional tone.
2.  **Answer Relevant Questions:** Only answer questions directly related to {CLIENT_NAME}, its location, and the services listed above. Examples: "What web development services do you offer?", "Do you do SEO?", "Where are you located?".
3.  **Use Provided Knowledge:** Base your answers *only* on the information provided in your knowledge base. Do not invent services or details.
4.  **Keep it Concise:** Provide brief and to-the-point answers.
5.  **Decline Irrelevant Questions:** If a user asks a question outside the scope of {CLIENT_NAME}'s business (e.g., "What's the weather?", "Tell me a joke?", "Who is the president?", "Write me a poem"), politely state that you can only answer questions about {CLIENT_NAME} and its services. Do not attempt to answer the irrelevant question. Example refusal: "I can only assist with questions about Akhand Solutions and our services like website development and digital marketing. How can I help you with that?"
6.  **Do Not Hallucinate:** If you don't know the answer based on the provided knowledge, say you don't have that specific information but can talk about the known services.
"""

app = FastAPI(
    title="Akhand Solutions Chatbot API",
    description="A simple backend API for a Groq-powered chatbot.",
    version="1.0.0",
)

if GROQ_API_KEY:
    try:
        groq_client = Groq(api_key=GROQ_API_KEY)
        print("Groq client initialized successfully.")
        USE_MOCK_GROQ = False
    except Exception as e:
        print(f"Error initializing Groq client: {e}. Falling back to mock response.")
        groq_client = None
        USE_MOCK_GROQ = True
else:
    groq_client = None
    USE_MOCK_GROQ = True


# Pydantic Models for Request and Response
class UserQuery(BaseModel):
    query: str = Field(..., description="The query text from the user.")

class ChatResponse(BaseModel):
    response: str = Field(..., description="The chatbot's response.")

# --- Helper Function for Groq Interaction (or Mock) ---
async def get_groq_response(user_query: str) -> str:
    """
    Gets a response from Groq AI based on the user query and system prompt,
    or returns a mock response if Groq is unavailable.
    """
    if USE_MOCK_GROQ or not groq_client:
        print("Using Mock Groq Response")
        # Simple keyword-based mock logic
        query_lower = user_query.lower()
        if any(keyword in query_lower for keyword in ["website", "develop", "design", "e-commerce"]):
            return f"As a representative of {CLIENT_NAME}, we offer various website development services including custom sites and e-commerce platforms. How can I provide more details?"
        elif any(keyword in query_lower for keyword in ["marketing", "seo", "smm", "ppc"]):
            return f"Yes, {CLIENT_NAME} provides digital marketing services like SEO, SMM, and PPC management. What specific service are you interested in?"
        elif any(keyword in query_lower for keyword in ["location", "where", "pune"]):
             return f"{CLIENT_NAME} is located in {CLIENT_LOCATION}."
        elif any(keyword in query_lower for keyword in ["weather", "joke", "time", "president", "poem", "capital"]):
             return f"I can only assist with questions about {CLIENT_NAME} and our services. How can I help you with website development or digital marketing?"
        else:
            return f"Thanks for your question! As an AI assistant for {CLIENT_NAME}, I can tell you about our services like website development and digital marketing. What are you looking for?"

    # --- Actual Groq API Call ---
    try:
        print(f"Sending to Groq - User Query: {user_query}")
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": user_query,
                },
            ],
            # model="mixtral-8x7b-32768", # Or choose another model like llama3-8b-8192
            model="llama3-8b-8192",
            temperature=0.7,  # Adjust for creativity vs. factuality
            max_tokens=150,    # Limit response length
            stop=None,        # Can add stop sequences if needed
            stream=False,
        )
        response_content = chat_completion.choices[0].message.content
        print(f"Received from Groq: {response_content}")
        return response_content

    except GroqError as e:
        print(f"Groq API Error: {e}")
        raise HTTPException(status_code=500, detail=f"Groq API error: {e.message}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal server error interacting with AI service.")


@app.post("/chat", response_model=ChatResponse)
async def handle_chat(user_query: UserQuery):
    """
    Receives a user query via POST request and returns
    a response generated by Groq AI based on Akhand Solutions' context.
    """
    print(f"Received query: {user_query.query}")

    if not user_query.query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    try:
        # Get the response from Groq (or mock)
        bot_response = await get_groq_response(user_query.query)
        return ChatResponse(response=bot_response)

    except HTTPException as http_exc:
        # Re-raise HTTPExceptions (like 500 errors from Groq helper)
        raise http_exc
    except Exception as e:
        # Catch any other unexpected errors
        print(f"Error during chat handling: {e}")
        raise HTTPException(status_code=500, detail="An internal server error occurred.")


@app.get("/")
async def root():
    return {"message": f"Welcome to the {CLIENT_NAME} Chatbot API. Use the /chat endpoint (POST) to interact."}


#
if __name__ == "__main__":
    print("Starting FastAPI server...")
    # Use reload=True for development to automatically reload on code changes
    uvicorn.run("chatbot_backend:app", host="0.0.0.0", port=8000, reload=True)
    # uvicorn.run(app, host="0.0.0.0", port=8000)