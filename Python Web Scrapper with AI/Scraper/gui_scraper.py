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
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
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


def parse_business_data(driver):
    wait = WebDriverWait(driver, 10)
    business_data = []

    businesses = driver.find_elements(By.CSS_SELECTOR, 'div.Nv2PK, div[role="article"]')
    print(f"Found {len(businesses)} businesses")

    for i, business in enumerate(businesses, 1):
        try:
            print(f"Processing business {i}/{len(businesses)}")
            
            # Click the business to open details panel
            driver.execute_script("arguments[0].scrollIntoView(true);", business)
            time.sleep(1)
            business.click()
            time.sleep(2)

            # Wait for details panel with multiple possible selectors
            try:
                details_div = wait.until(EC.presence_of_element_located((
                    By.CSS_SELECTOR, 
                    'div.m6QErb.DxyBCb.kA9KIf.dS8AEf, div.m6QErb.DxyBCb.kA9KIf, div[role="main"]'
                )))
            except:
                print("Could not find details panel, trying alternative approach...")
                continue

            data = {
                'Name': '',
                'Category': '',
                'Rating': '',
                'Reviews': '',
                'Address': '',
                'Phone': '',
                'Email': '',
                'Website': 'No website',
                'GoogleMapsUrl': driver.current_url
            }

            # Extract name with multiple possible selectors
            try:
                name_elem = details_div.find_element(By.CSS_SELECTOR, 'h1 .fontHeadlineLarge, h1 span, .DUwDvf')
                data['Name'] = name_elem.text.strip()
            except:
                try:
                    name_elem = business.find_element(By.CSS_SELECTOR, '.fontHeadlineLarge, .qBF1Pd')
                    data['Name'] = name_elem.text.strip()
                except:
                    print("Could not find business name")
                    continue

            # Extract contact information
            try:
                info_elements = details_div.find_elements(By.CSS_SELECTOR, 'div[data-item-id], button[data-item-id]')
                for elem in info_elements:
                    text = elem.get_attribute('aria-label') or elem.text
                    if text:
                        if 'Address' in text:
                            data['Address'] = text.replace('Address:', '').strip()
                        elif 'Phone' in text:
                            data['Phone'] = text.replace('Phone:', '').strip()
            except Exception as e:
                print(f"Error extracting contact info: {e}")

            # Extract website
            try:
                website_elem = details_div.find_element(By.CSS_SELECTOR, 'a[data-item-id*="website"], a[aria-label*="website"]')
                data['Website'] = website_elem.get_attribute('href')
            except:
                pass

            # Only append if we have at least a name
            if data['Name']:
                business_data.append(data)
                print(f"Successfully extracted data for: {data['Name']}")

        except Exception as e:
            print(f"Error processing business: {str(e)}")
            continue

    return business_data


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
                    print(f"\nSaving {len(all_results)} leads to {OUTPUT_FILE}...")
                    df.to_excel(OUTPUT_FILE, index=False, engine='openpyxl')
                    print(f"Successfully saved leads to {OUTPUT_FILE}")
                except Exception as e:
                    print(f"\nError saving data to Excel: {e}")
                    try:
                        csv_file = OUTPUT_FILE.replace('.xlsx', '.csv')
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