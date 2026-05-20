import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

# Load environment variables from .env file
load_dotenv()

# Get the API key for Anthropic from environment variables
api_key = os.getenv("ANTHROPIC_API_KEY")

# The URL of the speaker page we want to scrape
url = "https://londontechweek.com/speakers/maliha-abidi"

# Fetch the page
response = requests.get(url)

# Print the status code so we know if it worked
print(f"Status code: {response.status_code}")

# Parse the HTML
soup = BeautifulSoup(response.text, "html.parser")

# Find the speaker's name - it's inside an h2 tag
name_tag = soup.find("h2")
name = name_tag.text.strip()

# Print it
print(f"Speaker name: {name}")

# Find the speaker's role/position
position_tag = soup.find("span", class_="m-speaker-entry__item__details__position")
position = position_tag.text.strip() if position_tag else "Unknown"

# Find the speaker's company
company_tag = soup.find("span", class_="m-speaker-entry__item__details__company")
company = company_tag.text.strip() if company_tag else "Unknown"

print(f"Position: {position}")
print(f"Company: {company}")

