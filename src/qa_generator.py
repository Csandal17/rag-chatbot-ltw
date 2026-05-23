import os
import json
import csv
import time
from dotenv import load_dotenv
from anthropic import Anthropic

# Load the API key from .env
load_dotenv()
client = Anthropic()

# --- Settings ---
MAX_ITEMS = 50         # Small test batch first. Raise to ~50 for the full run.
PAIRS_PER_ITEM = 3     # How many Q/A pairs to generate per item
SESSION_COUNT = 35     # When full: how many sessions to sample
SPEAKER_COUNT = 15     # When full: how many speakers to sample

# --- Load scraped data ---
with open("data/raw/sessions.json", "r", encoding="utf-8") as f:
    sessions = json.load(f)

with open("data/raw/speakers.json", "r", encoding="utf-8") as f:
    speakers = json.load(f)

# Build the list of items to process.
# For the test batch we just take the first few sessions.
# (We'll switch to proper sampling across both types for the full run.)
import random
random.seed(42)  # makes the sample reproducible — same items every run

# Sample a spread across both content types
sampled_sessions = random.sample(sessions, SESSION_COUNT)
sampled_speakers = random.sample(speakers, SPEAKER_COUNT)
items = sampled_sessions + sampled_speakers

def build_text(item):
    """Build a readable text block depending on whether item is a session or speaker."""
    if "title" in item:
        # It's a session
        return f"""Title: {item['title']}
Time: {item['time']}
Stage: {item['stage']}
Theme: {item['theme']}
Description: {item['description']}"""
    else:
        # It's a speaker
        return f"""Speaker: {item['name']}
Position: {item['position']}
Company: {item['company']}"""


def generate_pairs(item_text):
    """Ask Claude for Q/A pairs and return them as a parsed Python list."""
    prompt = f"""You are helping build a Q&A dataset for a chatbot about London Tech Week 2026.

Here is one item:

{item_text}

Generate {PAIRS_PER_ITEM} realistic question-and-answer pairs that an attendee might ask about THIS item.
Make the questions natural and varied. Keep answers factual and based only on the information above.

Return ONLY a valid JSON array, with no other text, no explanation, and no markdown code fences.
Each element must be an object with exactly two keys: "question" and "answer".

Example of the exact format:
[{{"question": "...", "answer": "..."}}, {{"question": "...", "answer": "..."}}]
"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}],
    )

    raw_text = response.content[0].text.strip()

    # Defensively strip markdown code fences if present
    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[len("json"):]
        raw_text = raw_text.strip()

    return json.loads(raw_text)


# --- Main loop ---
all_pairs = []

for i, item in enumerate(items, start=1):
    # A short label so we can see what's being processed
    label = item.get("title") or item.get("name") or "Unknown"
    print(f"[{i}/{len(items)}] Generating for: {label[:60]}")

    item_text = build_text(item)

    try:
        pairs = generate_pairs(item_text)
        for pair in pairs:
            all_pairs.append({
                "source": label,
                "question": pair["question"],
                "answer": pair["answer"],
            })
    except Exception as e:
        print(f"   ⚠️  Skipped (couldn't parse): {e}")

    time.sleep(0.5)  # polite delay between calls

print()
print(f"Collected {len(all_pairs)} Q/A pairs total.")

# --- Save to CSV ---
os.makedirs("data/processed", exist_ok=True)
output_path = "data/processed/qa_pairs.csv"

with open(output_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["source", "question", "answer"])
    writer.writeheader()
    writer.writerows(all_pairs)

print(f"Saved to {output_path}")
