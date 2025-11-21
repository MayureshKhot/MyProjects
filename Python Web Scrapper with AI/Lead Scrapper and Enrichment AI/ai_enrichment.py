import csv
import google.generativeai as genai
import os

# Set your Gemini API key
GOOGLE_API_KEY = "YOUR_GEMINI_API_KEY"
genai.configure(api_key=GOOGLE_API_KEY)

def enrich_with_ai(profile):
    prompt = f"""
You're an AI trained to analyze LinkedIn profile snippets.

PROFILE:
Name & Title: {profile['title']}
LinkedIn URL: {profile['url']}
Description: {profile['description']}

TASKS:
1. Summarize this profile in 1-2 sentences.
2. Categorize the person into one of the following: Entrepreneur, Executive, Healthcare, Tech, Student, Unknown.
3. Write a friendly LinkedIn outreach message to connect with this person (100 words max).
Return the result in a readable format.
"""
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"AI Error: {str(e)}"

def read_profiles(filename="linkedin_profiles.csv"):
    profiles = []
    with open(filename, newline='', encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            profiles.append(row)
    return profiles

def write_enriched_profiles(profiles, output_file="linkedin_profiles_enriched.csv"):
    fieldnames = ["title", "url", "description", "ai_enrichment"]
    with open(output_file, "w", newline='', encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for profile in profiles:
            writer.writerow(profile)
    print(f"[✓] Saved enriched data to: {output_file}")

def main():
    profiles = read_profiles()
    if not profiles:
        print("[!] No profiles found in CSV.")
        return

    print(f"[•] Enriching {len(profiles)} profiles with AI...")

    for i, profile in enumerate(profiles, 1):
        print(f"[{i}/{len(profiles)}] Enriching: {profile['title']}")
        enrichment = enrich_with_ai(profile)
        profile["ai_enrichment"] = enrichment

    write_enriched_profiles(profiles)

if __name__ == "__main__":
    main()
