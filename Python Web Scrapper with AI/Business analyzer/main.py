# main.py
import os
import time
import logging
import googlemaps
import pandas as pd
from dotenv import load_dotenv
from groq import Groq
from utils import fetch_website_content # Import from our helper file

# --- Configuration ---
load_dotenv()
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GOOGLE_MAPS_API_KEY:
    raise ValueError("GOOGLE_MAPS_API_KEY not found in .env file")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env file")

# Initialize Clients
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
groq_client = Groq(api_key=GROQ_API_KEY)

# Groq Model Configuration
GROQ_MODEL = "llama3-8b-8192" # Or choose another LLaMA model available on Groq

# Logging Setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Rate Limiting Delays (in seconds)
GOOGLE_MAPS_DELAY = 1
WEBSITE_FETCH_DELAY = 1
GROQ_API_DELAY = 2 # Be cautious with Groq's rate limits

# --- Core Functions ---

def search_places(query, max_results=10):
    """Searches Google Maps Places API using a text query."""
    logger.info(f"Searching Google Maps for: '{query}' (max_results={max_results})")
    places_result = []
    try:
        # Using text_search which is flexible for "keyword in location"
        response = gmaps.places(query=query)
        results = response.get('results', [])

        count = 0
        for place in results:
            if count >= max_results:
                break

            place_id = place.get('place_id')
            if not place_id:
                continue

            # Make a Place Details request to get website and formatted address
            details = gmaps.place(place_id=place_id, fields=['name', 'website', 'formatted_address'])
            place_details = details.get('result', {})

            business_info = {
                'name': place_details.get('name'),
                'address': place_details.get('formatted_address'),
                'website': place_details.get('website'),
                'place_id': place_id # Keep for reference if needed
            }

            # Basic validation
            if business_info['name'] and business_info['address']:
                 places_result.append(business_info)
                 count += 1
                 logger.info(f"Found: {business_info['name']}")
            else:
                 logger.warning(f"Skipping place due to missing name or address: {place.get('name')}")

            # Respect rate limits
            time.sleep(GOOGLE_MAPS_DELAY)

    except googlemaps.exceptions.ApiError as e:
        logger.error(f"Google Maps API Error: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during Google Maps search: {e}")

    logger.info(f"Found {len(places_result)} businesses matching criteria.")
    return places_result

def analyze_website_with_groq(title, meta_description, body_snippet, website_url):
    """Sends website content to Groq LLaMA for analysis."""
    if not title and not meta_description and not body_snippet:
        logger.warning(f"No content provided for analysis of {website_url}")
        return "Error: No content fetched from website to analyze."

    # Construct a clear prompt for the LLM
    prompt = f"""
    Analyze the following website information for a business website ({website_url}):

    Title: "{title}"
    Meta Description: "{meta_description}"
    Body Text Snippet (first 1000 chars): "{body_snippet}"

    Based *only* on the provided information, please identify potential issues and suggest improvements in these areas:

    1.  **Technical Issues:** (e.g., missing title, missing meta description, hints of poor structure if noticeable in snippet). Do not guess about performance or technologies not mentioned.
    2.  **SEO Improvements:** (e.g., Is the title descriptive? Is the meta description compelling? Does the snippet seem relevant?)
    3.  **Mobile Responsiveness Concerns:** (Based *only* on the text/structure provided, are there any red flags? e.g., mentions of "click here" which might be small targets, very long unformatted text blocks). Acknowledge limitations as you cannot see the layout.
    4.  **UI/UX Suggestions:** (e.g., Clarity of purpose based on title/description, readability hints from the text snippet). Acknowledge limitations.

    Provide a concise bullet-point summary for each category. If no specific issues are identifiable from the limited text, state that. Be factual based on the input.
    """

    logger.info(f"Sending request to Groq for: {website_url}")
    try:
        # Add delay before Groq API call
        time.sleep(GROQ_API_DELAY)

        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=GROQ_MODEL,
            temperature=0.3, # Lower temperature for more factual analysis
            max_tokens=500,  # Adjust as needed
            # top_p=1, # Defaults often work well
            # stop=None, # Defaults often work well
            # stream=False # Get the full response at once
        )
        analysis = chat_completion.choices[0].message.content
        logger.info(f"Groq analysis received for: {website_url}")
        return analysis.strip()

    except Exception as e:
        logger.error(f"Groq API Error for {website_url}: {e}")
        return f"Error: Failed to get analysis from Groq - {e}"

def save_to_excel(data, filename="output.xlsx"):
    """Saves the collected data to an Excel file."""
    if not data:
        logger.warning("No data to save.")
        return

    df = pd.DataFrame(data)
    try:
        df.to_excel(filename, index=False, engine='openpyxl')
        logger.info(f"Data successfully saved to {filename}")
    except Exception as e:
        logger.error(f"Failed to save data to Excel: {e}")

# --- Main Execution ---

def main():
    """Main function to orchestrate the process."""
    print("--- Business Website Analyzer ---")

    # --- User Input ---
    keyword = input("Enter the type of business (e.g., 'restaurants', 'plumbers'): ")
    location = input("Enter the location (e.g., 'New York, NY', '94107'): ")
    # Optional: Add radius input if needed, and switch to gmaps.places_nearby
    # radius_meters = input("Enter search radius in meters (e.g., 5000): ")
    try:
        max_results = int(input("Enter the maximum number of businesses to analyze (e.g., 10): "))
        if max_results <= 0:
            max_results = 10 # Default
            print("Invalid number, defaulting to 10 results.")
    except ValueError:
        max_results = 10 # Default
        print("Invalid input, defaulting to 10 results.")

    search_query = f"{keyword} in {location}"
    output_filename = f"{keyword.replace(' ','_')}_{location.replace(',','').replace(' ','_')}_analysis.xlsx"

    # --- Processing ---
    businesses = search_places(search_query, max_results)
    analysis_results = []

    if not businesses:
        print("No businesses found matching your criteria.")
        return

    print(f"\nFound {len(businesses)} businesses. Analyzing websites...")

    for business in businesses:
        logger.info(f"Processing: {business['name']}")
        website_url = business.get('website')
        analysis_summary = "N/A (No website listed)" # Default if no website

        if website_url:
            # Add delay before fetching website
            time.sleep(WEBSITE_FETCH_DELAY)
            _content, title, meta_desc, body_snippet = fetch_website_content(website_url)

            if title or meta_desc or body_snippet: # Only analyze if we got *something*
                 analysis_summary = analyze_website_with_groq(title, meta_desc, body_snippet, website_url)
            elif _content is None: # Fetch failed entirely
                 analysis_summary = "Error: Could not fetch website content."
            else: # Fetch succeeded but parsing failed to get key elements
                 analysis_summary = "Error: Could not parse key elements (title, meta) from website."

        analysis_results.append({
            "Business Name": business.get('name', 'N/A'),
            "Website URL": website_url if website_url else "N/A",
            "Address": business.get('address', 'N/A'),
            "LLM Analysis Summary": analysis_summary
        })

    # --- Output ---
    save_to_excel(analysis_results, output_filename)
    print(f"\nAnalysis complete. Results saved to '{output_filename}'")

if __name__ == "__main__":
    main()