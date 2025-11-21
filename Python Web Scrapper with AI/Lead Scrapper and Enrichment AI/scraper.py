from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv
import os


def get_linkedin_profiles_bing(keywords, max_pages=5, delay=3):
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from webdriver_manager.chrome import ChromeDriverManager
    import time

    query = "site:linkedin.com/in/ " + " ".join(keywords)
    query_encoded = query.replace(" ", "+")

    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    profiles = []

    print(f"Searching Bing for: {query}")

    for page in range(max_pages):
        offset = page * 10 + 1
        search_url = f"https://www.bing.com/search?q={query_encoded}&first={offset}"
        print(f"Scraping page {page + 1}: {search_url}")
        driver.get(search_url)
        time.sleep(delay)

        results = driver.find_elements(By.CSS_SELECTOR, "li.b_algo")
        new_results = 0

        for result in results:
            try:
                # Extract the headline text (this is the proper profile title)
                title_element = result.find_element(By.CSS_SELECTOR, "h2 a")
                title = title_element.text.strip() if title_element else "No Title"
                url = title_element.get_attribute("href") if title_element else None

                # Clean tracking parameters from URL if needed
                if url:
                    url = url.split("?")[0]

                # Extract the snippet/description
                try:
                    snippet_tag = result.find_element(By.TAG_NAME, "p")
                    description = snippet_tag.text.strip()
                except:
                    description = ""

                # Save only real LinkedIn profile URLs
                if url and "linkedin.com/in/" in url:
                    profiles.append({
                        "title": title,
                        "url": url,
                        "description": description
                    })

            except Exception as e:
                continue



        if new_results == 0:
            print("No more results found. Stopping.")
            break

    driver.quit()
    print(f"Total LinkedIn profiles collected: {len(profiles)}")
    return profiles


def save_to_csv(profiles, filename="linkedin_profiles.csv"):
    if not profiles:
        print("No profiles found to save.")
        return

    file_exists = os.path.isfile(filename)
    file_empty = not file_exists or os.stat(filename).st_size == 0

    with open(filename, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "url", "description"])
        if file_empty:
            writer.writeheader()
        writer.writerows(profiles)

    print(f"Appended {len(profiles)} profiles to {filename}")


if __name__ == "__main__":
    print("--- LinkedIn Profile Scraper (Bing Edition) ---")
    keywords_input = input("Enter keywords: ").strip()

    if not keywords_input:
        print("No keywords provided. Exiting.")
    else:
        keywords = keywords_input.split()
        # profiles = get_linkedin_profiles_bing(keywords)
        profiles = get_linkedin_profiles_bing(keywords, max_pages=1, delay=3)
        if profiles:
            save_to_csv(profiles)
