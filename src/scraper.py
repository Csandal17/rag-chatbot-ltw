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

def get_session_urls(sitemap_url, limit=300):
    """Fetch the agenda sitemap and return a list of session URLs."""
    response = requests.get(sitemap_url)
    soup = BeautifulSoup(response.text, "lxml-xml")

    loc_tags = soup.find_all("loc")
    urls = [tag.text for tag in loc_tags]

    print(f"Found {len(urls)} session URLs in sitemap")
    return urls[:limit]

def scrape_session(url):
    """Fetch an agenda session page and extract its details."""
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to fetch {url} (status {response.status_code})")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # Title - use the og:title meta tag (clean, no site suffix)
    title_tag = soup.find("meta", attrs={"property": "og:title"})
    title = title_tag["content"].strip() if title_tag else "Unknown"

    # Time
    time_tag = soup.find("time")
    session_time = time_tag.text.strip() if time_tag else "Unknown"

    # Stage / location
    location_tag = soup.find("div", class_="m-seminar-entry__item__details__location")
    stage = location_tag.text.strip() if location_tag else "Unknown"

    # Theme / stream
    stream_tag = soup.find("span", class_="m-seminar-entry__item__details__stream__name")
    theme = stream_tag.text.strip() if stream_tag else "Unknown"

    # Description - paragraph + bullets, flattened into clean text
    desc_tag = soup.find("div", class_="m-seminar-entry__item__description")
    description = desc_tag.get_text(separator=" ", strip=True) if desc_tag else "Unknown"

    return {
        "url": url,
        "title": title,
        "time": session_time,
        "stage": stage,
        "theme": theme,
        "description": description,
    }

# Get a list of session URLs from the agenda sitemap
agenda_sitemap = "https://londontechweek.com/__media/sitemap_agenda.xml"
session_urls = get_session_urls(agenda_sitemap)

# Scrape each session and collect the results
sessions = []
for i, url in enumerate(session_urls, start=1):
    print(f"[{i}/{len(session_urls)}] Scraping {url}...")
    session_data = scrape_session(url)
    if session_data:
        sessions.append(session_data)
    time.sleep(0.5)  # Be polite

# Save to JSON
output_path = "data/raw/sessions.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(sessions, f, indent=2, ensure_ascii=False)

print(f"\nSuccessfully scraped {len(sessions)} sessions")
print(f"Saved to {output_path}")

# # --- Clean the sessions data: remove non-session index pages ---
# import json

# with open("data/raw/sessions.json", "r", encoding="utf-8") as f:
#     sessions = json.load(f)

# # Keep only real sessions (those with a known stage)
# clean_sessions = [s for s in sessions if s["stage"] != "Unknown"]

# with open("data/raw/sessions.json", "w", encoding="utf-8") as f:
#     json.dump(clean_sessions, f, indent=2, ensure_ascii=False)

# print(f"Cleaned: kept {len(clean_sessions)} sessions, removed {len(sessions) - len(clean_sessions)}")
