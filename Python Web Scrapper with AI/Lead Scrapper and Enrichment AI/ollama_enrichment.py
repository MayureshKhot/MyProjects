import csv
import requests
import os

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:3b"  

def enrich_with_ollama(profile):
    prompt = f"""
Given the following LinkedIn profile data:

Title: {profile['title']}
URL: {profile['url']}
Description: {profile['description']}

Extract and return the following fields as a JSON object:

{{
  "name": "Full name of the person (if available)",
  "profession": "Their likely profession or category",
  "summary": "1-2 sentence summary of the profile",
  "outreach_message": "A personalized LinkedIn connection message (4-5 sentences, each under 15 words) that starts with a personal comment about their work/role, mentions their specific profession, offers genuine value through a free LinkedIn growth roadmap, and includes a simple call-to-action. Keep the tone conversational, friendly, and helpful. Make it feel personal and relevant to their background."
}}

Return only the JSON object and nothing else.
"""
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        raw_text = response.json().get("response", "").strip()

        # Try parsing the response as JSON
        try:
            return json.loads(raw_text)
        except Exception as e:
            print(f"[!] Warning: Failed to parse JSON. Raw response: {raw_text}")
            return {"summary": raw_text, "name": "", "profession": "", "outreach_message": ""}

    except Exception as e:
        return {"summary": f"Ollama Error: {e}", "name": "", "profession": "", "outreach_message": ""}

def read_profiles(filename="linkedin_profiles.csv"):
    profiles = []
    with open(filename, newline='', encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            profiles.append(row)
    return profiles

def write_enriched_profiles(profiles, output_file="linkedin_profiles_enriched.csv"):
    """
    Appends enriched profile data to a CSV file.
    If the file doesn't exist, it creates it and adds headers.
    """
    file_exists = os.path.isfile(output_file)
    
    # Define the headers
    fieldnames = ["title", "url", "description", "name", "profession", "summary", "outreach_message"]

    try:
        with open(output_file, mode="a", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()  # Write headers only if file is new

            writer.writerows(profiles)

        print(f"[✓] Appended {len(profiles)} enriched profiles to {output_file}")
    except IOError as e:
        print(f"[!] Failed to write to file: {e}")



# for entire dataset.
# def main():
#     profiles = read_profiles()
#     if not profiles:
#         print("[!] No profiles found in CSV.")
#         return

#     print(f"[•] Enriching {len(profiles)} profiles using Ollama...")

#     for i, profile in enumerate(profiles, 1):
#         print(f"[{i}/{len(profiles)}] Enriching: {profile['title']}")
#         enrichment = enrich_with_ollama(profile)
#         profile["ai_enrichment"] = enrichment

#     write_enriched_profiles(profiles)

# test 5 profiles
def main():
    profiles = read_profiles()
    if not profiles:
        print("[!] No profiles found.")
        return

    print(f"[•] Enriching first 5 of {len(profiles)} profiles using Ollama...")

    test_profiles = profiles[:5]

    for i, profile in enumerate(test_profiles, 1):
        print(f"[{i}/5] Processing: {profile['title']}")
        ai_output = enrich_with_ollama(profile)

        profile["name"] = ai_output.get("name", "")
        profile["profession"] = ai_output.get("profession", "")
        profile["summary"] = ai_output.get("summary", "")
        profile["outreach_message"] = ai_output.get("outreach_message", "")

    write_enriched_profiles(test_profiles, output_file="linkedin_profiles_enriched_sample.csv")


if __name__ == "__main__":
    main()
