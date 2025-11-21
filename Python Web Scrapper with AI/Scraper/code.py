import time
import pandas as pd
import os
import json
import re # For extracting rating/reviews cleanly
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from groq import Groq, RateLimitError

# --- Configuration ---
# Use headless mode (True) or show the browser window (False)
HEADLESS_MODE = False
# Maximum number of scrolls to load results (adjust as needed)
MAX_SCROLLS = 5
# Time to wait between scrolls (seconds) - Increase if results don't load fast enough
SCROLL_PAUSE_TIME = 3
# Time to wait for elements to appear (seconds)
WAIT_TIMEOUT = 10
# Output Excel file name
OUTPUT_FILE = "google_maps_leads_formatted.xlsx"
# Groq LLM Model
LLM_MODEL = "llama3-8b-8192" # Or "llama3-70b-8192" if needed, potentially slower/more rate limited
# Max retries for Groq API rate limits
GROQ_MAX_RETRIES = 3
GROQ_RETRY_DELAY = 5 # Seconds

# --- Groq API Setup ---
try:
    GROQ_API_KEY = "enter your api key"
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY environment variable not set.")
    groq_client = Groq(api_key=GROQ_API_KEY)
    print("Groq client initialized.")
except Exception as e:
    print(f"Error initializing Groq client: {e}")
    print("Please ensure the 'groq' library is installed (pip install groq)")
    print("And the GROQ_API_KEY environment variable is set correctly.")
    groq_client = None # Disable LLM features if setup fails

def setup_driver():
    """Sets up the Selenium WebDriver."""
    print("Setting up WebDriver...")
    options = webdriver.ChromeOptions()
    if HEADLESS_MODE:
        options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument("--lang=en-US")

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        print("WebDriver setup complete.")
        return driver
    except Exception as e:
        print(f"Error setting up WebDriver: {e}")
        return None

def scroll_results_panel(driver):
    """Scrolls the results panel to load more businesses."""
    print(f"Scrolling results panel (max {MAX_SCROLLS} times)...")
    try:
        scrollable_div = WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='feed']"))
        )
        print("Scrollable element found.")
    except TimeoutException:
        print("Error: Could not find the scrollable results panel.")
        return

    last_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
    scroll_count = 0
    no_change_count = 0 # Counter for consecutive scrolls with no height change

    while scroll_count < MAX_SCROLLS:
        print(f"Scrolling attempt {scroll_count + 1}/{MAX_SCROLLS}...")
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
        time.sleep(SCROLL_PAUSE_TIME)

        new_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
        if new_height == last_height:
            no_change_count += 1
            print("Scroll height didn't change.")
            if no_change_count >= 2: # Exit if height hasn't changed for 2 consecutive scrolls
                 print("Reached end of scrollable results (height stable).")
                 break
        else:
            no_change_count = 0 # Reset counter if height changes
            last_height = new_height

        scroll_count += 1
        # Check for the "You've reached the end of the list." message (selector might change)
        try:
            end_msg = driver.find_element(By.XPATH, "//*[contains(text(), \"You've reached the end of the list\")]")
            if end_msg.is_displayed():
                print("Found 'end of list' message.")
                break
        except NoSuchElementException:
            pass # Message not found, continue scrolling

    print("Scrolling finished.")


def parse_with_llm(text_block):
    """Uses Groq LLM to parse text for structured data."""
    if not groq_client or not text_block:
        return None # Return None if Groq client isn't setup or text is empty

    prompt = f"""
    Analyze the following text scraped from a Google Maps business listing.
    Extract the following information if present:
    - Phone Number (only the number, format consistently e.g., +1 XXX-XXX-XXXX or XXX-XXX-XXXX)
    - Email Address (if explicitly mentioned, which is rare)
    - Full Address (including street, city, state/province, postal code, country if available)
    - Business Category (e.g., Restaurant, Plumber, Cafe)

    If a piece of information is not found, use null or an empty string for its value.
    Return the result ONLY as a valid JSON object with the keys "phone", "email", "address", "category".

    Text to analyze:
    ---
    {text_block}
    ---

    JSON Output:
    """

    retries = 0
    while retries < GROQ_MAX_RETRIES:
        try:
            chat_completion = groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=LLM_MODEL,
                temperature=0.2, # Lower temperature for more deterministic output
                response_format={"type": "json_object"}, # Request JSON output directly
            )
            response_content = chat_completion.choices[0].message.content
            # print(f"LLM Raw Response: {response_content}") # Debugging
            parsed_json = json.loads(response_content)
            return parsed_json

        except RateLimitError:
            retries += 1
            print(f"Rate limit hit. Retrying in {GROQ_RETRY_DELAY}s... ({retries}/{GROQ_MAX_RETRIES})")
            time.sleep(GROQ_RETRY_DELAY)
        except json.JSONDecodeError:
             print(f"Error: LLM did not return valid JSON: {response_content}")
             return None # Failed to parse JSON
        except Exception as e:
            print(f"Error during Groq API call: {e}")
            return None # Other API errors

    print("Max retries reached for Groq API. Skipping LLM parsing for this item.")
    return None


def parse_business_data(driver, use_ai=True, groq_client=None):
    """Parses business data, using LLM for specific fields if enabled."""
    print("Parsing business data...")
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    results = []

    # Update selectors to match current Google Maps structure
    business_elements = soup.find_all('div', {'jsaction': lambda x: x and 'mouseover' in x})
    if not business_elements:
        business_elements = soup.find_all('div', {'class': lambda x: x and ('m6QErb' in x or 'Nv2PK' in x)})
    
    print(f"Found {len(business_elements)} potential business elements.")
    if not business_elements:
        print("Warning: Could not find business listing elements. Trying additional selectors...")
        # Try another common selector pattern
        business_elements = soup.find_all('div', {'class': lambda x: x and ('DxyBCb' in x or 'THOPZb' in x)})
        print(f"Additional search found {len(business_elements)} elements.")

    if not business_elements:
        print("Warning: Could not find business listing elements. Selectors need update.")
        return []

    for i, elem in enumerate(business_elements):
        print(f"\nProcessing element {i+1}/{len(business_elements)}...")
        data = {
            'Name': None,
            'Rating': None,
            'Reviews': None,
            'Category': None,
            'Address': None,
            'Phone': None,
            'Email': None, # Add email field
            'Website': 'No website', # Default to 'No website'
            'GoogleMapsUrl': None
        }

        # --- Direct Extraction (More Reliable Fields) ---
        # Name and Google Maps URL (Often found together in main link)
        try:
            link_tag = elem.find('a', {'aria-label': True, 'href': True})
            if link_tag and link_tag['href'].startswith('https://www.google.com/maps/place/'):
                 data['Name'] = link_tag['aria-label'].strip()
                 data['GoogleMapsUrl'] = link_tag['href']
            # Fallback if aria-label isn't the name (sometimes it's just address)
            elif link_tag:
                 # Try finding name in a specific div class nearby (e.g., fontHeadlineSmall)
                 name_div = elem.find('div', class_=lambda x: x and x.startswith('fontHeadline'))
                 if name_div:
                     data['Name'] = name_div.text.strip()
                 data['GoogleMapsUrl'] = link_tag['href'] # Still grab URL

            # If still no name, try another common pattern
            if not data['Name']:
                 name_tag = elem.find(['h1', 'h2', 'div'], class_=re.compile(r'fontTitle|fontHeadline')) # Broader search
                 if name_tag:
                     data['Name'] = name_tag.text.strip()

        except Exception as e:
            print(f"  - Error extracting name/URL: {e}")

        if not data['Name']:
            print("  - Skipping element: Could not reliably extract Name.")
            continue # Essential field missing

        print(f"  > Name: {data['Name']}")

        # Rating & Reviews
        try:
            rating_span = elem.find('span', {'role': 'img', 'aria-label': True})
            if rating_span and 'aria-label' in rating_span.attrs:
                aria_label = rating_span['aria-label']
                rating_match = re.search(r'(\d\.?\d*)\s+Stars', aria_label, re.IGNORECASE)
                reviews_match = re.search(r'(\d{1,3}(?:,\d{3})*|\d+)\s+Reviews', aria_label, re.IGNORECASE)
                if rating_match: data['Rating'] = float(rating_match.group(1))
                if reviews_match: data['Reviews'] = int(reviews_match.group(1).replace(',', ''))
                # print(f"  > Rating: {data['Rating']}, Reviews: {data['Reviews']}") # Debug
        except Exception as e:
            print(f"  - Error extracting rating/reviews: {e}")


        # Website (Direct link check is usually best)
        try:
            # Look for specific attributes like data-tooltip or aria-label containing 'Website'
            website_link = elem.find('a', {'data-tooltip': re.compile(r'Website|Visit website', re.I), 'href': True})
            if not website_link: # Fallback: Check aria-label
                 website_link = elem.find('a', {'aria-label': re.compile(r'Website|Visit website', re.I), 'href': True})
            # Fallback: Check for link near a globe icon (more complex selector needed)

            if website_link and website_link['href'] and not website_link['href'].startswith(('tel:', 'mailto:')):
                data['Website'] = website_link['href']
                print(f"  > Website Found: {data['Website']}")
            # else: # Keep default 'No website' if no link found
            #     print("  > Website: No website found via direct selectors.") # Debug
        except Exception as e:
            print(f"  - Error extracting website: {e}")


        # --- Text Aggregation and LLM Parsing ---
        details_text = ""
        if use_ai:
            # Existing text aggregation code
            potential_details_elements = elem.find_all(['div', 'span'], recursive=True)
            ignore_texts = [data['Name']] if data['Name'] else []
            if rating_span: ignore_texts.append(rating_span.text.strip())

            for detail_elem in potential_details_elements:
                elem_text = detail_elem.text.strip()
                if elem_text and elem_text not in ignore_texts and not elem_text.replace('.','',1).isdigit():
                    parent_a = detail_elem.find_parent('a')
                    if not (parent_a and parent_a == link_tag and elem_text == data['Name']):
                        details_text += elem_text + " | "

            details_text = details_text.strip().rstrip('|').strip()

            # LLM Processing if enabled and client available
            if details_text and groq_client:
                print("  - Sending text to LLM for parsing...")
                llm_result = parse_with_llm(details_text)
                
                if llm_result:
                    print(f"  - LLM Result: {llm_result}")
                    data['Phone'] = llm_result.get('phone') or data['Phone']
                    data['Email'] = llm_result.get('email') or data['Email']
                    data['Address'] = llm_result.get('address') or data['Address']
                    data['Category'] = llm_result.get('category') or data['Category']
        else:
            # Basic extraction without AI
            try:
                # Try to find address
                address_elem = elem.find('div', {'class': lambda x: x and 'address' in x.lower()})
                if address_elem:
                    data['Address'] = address_elem.text.strip()

                # Try to find phone using regex
                text_content = elem.get_text()
                phone_match = re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text_content)
                if phone_match:
                    data['Phone'] = phone_match.group(0)

                # Try to find category
                category_elem = elem.find('div', {'class': lambda x: x and 'category' in x.lower()})
                if category_elem:
                    data['Category'] = category_elem.text.strip()
            except Exception as e:
                print(f"  - Error in basic extraction: {e}")

        # --- Final Data Append ---
        # Clean up empty strings from LLM potentially
        for key in ['Phone', 'Email', 'Address', 'Category']:
             if data[key] == "": data[key] = None

        results.append(data)
        # Optional delay between processing items to reduce load/detection risk
        # time.sleep(0.5)

    print(f"\nParsing complete. Extracted data for {len(results)} businesses.")
    return results


def search_google_maps(driver, query, location):
    """Performs the search on Google Maps."""
    print(f"Searching for '{query}' in '{location}'...")
    # Encode query and location properly for URL
    from urllib.parse import quote_plus
    search_url = f"https://www.google.com/maps/search/{quote_plus(query)}+in+{quote_plus(location)}"
    print(f"Navigating to: {search_url}")
    try:
        driver.get(search_url)
        WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='feed'], div[aria-label*='Results for']"))
        )
        print("Search results page loaded.")
        # Add a small delay after load
        time.sleep(2)
        return True
    except TimeoutException:
        print("Error: Timed out waiting for search results page to load.")
        try:
            if "consent.google.com" in driver.current_url:
                 print("!! Detected consent page. Manual intervention might be needed if script hangs.")
                 print("   Try accepting cookies in the browser window if not headless.")
            elif driver.find_element(By.XPATH, "//*[contains(text(), 'No results found')]").is_displayed():
                print("Search returned no results.")
            else:
                 print("Page did not load expected results container.")
        except NoSuchElementException:
             print("Could not determine reason for timeout. Check selectors or network.")
        return False
    except Exception as e:
        print(f"An error occurred during navigation: {e}")
        return False


# --- Main Execution ---
# Add this function near the top with other helper functions
def get_unique_filename(base_filename):
    """Generate a unique filename by adding (1), (2), etc. if file exists."""
    if not os.path.exists(base_filename):
        return base_filename
    
    name, ext = os.path.splitext(base_filename)
    counter = 1
    while True:
        new_filename = f"{name}({counter}){ext}"
        if not os.path.exists(new_filename):
            return new_filename
        counter += 1

# In the main execution block, modify the Excel saving section:
if __name__ == "__main__":
    if not groq_client:
        print("\nGroq client not available. LLM parsing will be disabled.")
        # Decide if you want to proceed without LLM or exit
        # exit() # Uncomment to exit if LLM is essential

    search_query = input("Enter the search query (e.g., 'restaurants', 'plumbers'): ")
    search_location = input("Enter the location (e.g., 'New York', 'London UK'): ")

    driver = setup_driver()

    if driver:
        all_results = []
        if search_google_maps(driver, search_query, search_location):
            scroll_results_panel(driver)
            all_results = parse_business_data(driver)

            if all_results:
                df = pd.DataFrame(all_results)

                # Define desired column order
                cols = ['Name', 'Category', 'Rating', 'Reviews', 'Address', 'Phone', 'Email', 'Website', 'GoogleMapsUrl']
                # Filter to only include columns that actually exist in the DataFrame
                df = df[[col for col in cols if col in df.columns]]

                try:
                    output_file = get_unique_filename(OUTPUT_FILE)
                    print(f"\nSaving {len(all_results)} leads to {output_file}...")
                    df.to_excel(output_file, index=False, engine='openpyxl')
                    print(f"Successfully saved leads to {output_file}")
                except Exception as e:
                    print(f"\nError saving data to Excel: {e}")
                    try:
                        csv_file = get_unique_filename(output_file.replace('.xlsx', '.csv'))
                        print(f"Attempting to save as CSV: {csv_file}")
                        df.to_csv(csv_file, index=False)
                        print(f"Successfully saved leads to {csv_file}.")
                    except Exception as csv_e:
                        print(f"Could not save to CSV either: {csv_e}")
            else:
                print("\nNo business data could be extracted. Check selectors or search terms.")
        else:
            print("\nSearch failed or returned no results. Could not proceed.")

        print("Closing WebDriver...")
        driver.quit()
    else:
        print("Could not start WebDriver. Exiting.")

    print("Script finished.")
