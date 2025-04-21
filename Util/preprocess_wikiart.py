import pandas as pd
import json
from colorthief import ColorThief
import requests
from io import BytesIO

# Load the CSV file
df = pd.read_csv("data/wikiart_scraped.csv")
df.columns = df.columns.str.strip()
df = df.dropna(subset=['Link'])  # remove rows without image links

# Optional: limit for testing (remove later)
df = df.head(50)

artworks = []

for _, row in df.iterrows():
    image_url = row['Link']
    try:
        # Download the image and extract dominant colors
        response = requests.get(image_url, timeout=5)
        img = BytesIO(response.content)
        color_thief = ColorThief(img)
        dominant_color = color_thief.get_color(quality=1)
        palette = color_thief.get_palette(color_count=6)

        # Build artwork entry
        artwork = {
            "title": row["Artwork"],
            "artist": row["Artist"],
            "style": row["Style"],
            "date": row["Date"],
            "image_url": image_url,
            "dominant_color": dominant_color,
            "palette": palette
        }
        artworks.append(artwork)
    except Exception as e:
        print(f"⚠️ Skipped '{row['artwork']}' due to error: {e}")

# Save to a JSON file
with open("data/wikiart_processed.json", "w") as f:
    json.dump(artworks, f, indent=2)

# After cleaning and processing your DataFrame (df)
df.to_json('cleaned_wikiart_data.json', orient='records', lines=True)
