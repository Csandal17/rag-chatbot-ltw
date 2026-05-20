import os
import time
import json
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

# Load environment variables from .env file
load_dotenv()

# Get the API key for Anthropic from environment variables
api_key = os.getenv("ANTHROPIC_API_KEY")

# # The URL of the speaker page we want to scrape
# url = "https://londontechweek.com/speakers/maliha-abidi"

# # Fetch the page
# response = requests.get(url)

# # Print the status code so we know if it worked
# print(f"Status code: {response.status_code}")

# # Parse the HTML
# soup = BeautifulSoup(response.text, "html.parser")

# # Find the speaker's name - it's inside an h2 tag
# name_tag = soup.find("h2")
# name = name_tag.text.strip()

# # Print it
# print(f"Speaker name: {name}")

# # Find the speaker's role/position
# position_tag = soup.find("span", class_="m-speaker-entry__item__details__position")
# position = position_tag.text.strip() if position_tag else "Unknown"

# # Find the speaker's company
# company_tag = soup.find("span", class_="m-speaker-entry__item__details__company")
# company = company_tag.text.strip() if company_tag else "Unknown"

# print(f"Position: {position}")
# print(f"Company: {company}")

def scrape_speaker(url):
    """Fetch a speaker page and extract their details."""
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Failed to fetch {url} (status {response.status_code})")
        return None
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    name_tag = soup.find("h2")
    name = name_tag.text.strip() if name_tag else "Unknown"
    
    position_tag = soup.find("span", class_="m-speaker-entry__item__details__position")
    position = position_tag.text.strip().rstrip(",") if position_tag else "Unknown"
    
    company_tag = soup.find("span", class_="m-speaker-entry__item__details__company")
    company = company_tag.text.strip() if company_tag else "Unknown"
    
    return {
        "url": url,
        "name": name,
        "position": position,
        "company": company,
    }

def get_speaker_urls(sitemap_url, limit=50):
    """Fetch the speaker sitemap and return a list of URLs."""
    response = requests.get(sitemap_url)
    soup = BeautifulSoup(response.text, "lxml-xml")
    
    # Find all <loc> tags - each contains one URL
    loc_tags = soup.find_all("loc")
    urls = [tag.text for tag in loc_tags]
    
    print(f"Found {len(urls)} speaker URLs in sitemap")
    
    # Return only the first `limit` URLs
    return urls[:limit]

# Get a list of speaker URLs from the sitemap
sitemap_url = "https://londontechweek.com/__media/sitemap_speakers.xml"
speaker_urls = get_speaker_urls(sitemap_url, limit=50)

# Scrape each speaker and collect the results
speakers = []
for i, url in enumerate(speaker_urls, start=1):
    print(f"[{i}/{len(speaker_urls)}] Scraping {url}...")
    speaker_data = scrape_speaker(url)
    if speaker_data:
        speakers.append(speaker_data)
    time.sleep(0.5)  # Be polite - pause half a second between requests

# Save to JSON
output_path = "data/raw/speakers.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(speakers, f, indent=2, ensure_ascii=False)

print(f"\nSuccessfully scraped {len(speakers)} speakers")
print(f"Saved to {output_path}")