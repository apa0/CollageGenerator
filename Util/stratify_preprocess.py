import pandas as pd
import requests
import json
from io import BytesIO
from colorthief import ColorThief

# New preprocessing script, removes duplicate URLS, stratifying by style to ensure sample is diverse

# Load the CSV file
df = pd.read_csv("data/wikiart_scraped.csv")
df.columns = df.columns.str.strip()

# Drop rows without image links
df = df.dropna(subset=['Link'])

# Group by style and sample up to 3 artworks per style
grouped = df.groupby('Style')
sampled_df = grouped.apply(lambda x: x.sample(n=min(3, len(x)), random_state=42)).reset_index(drop=True)

# Remove duplicate image URLs
sampled_df = sampled_df.drop_duplicates(subset=['Link'])

# Optional: limit total sample size
sampled_df = sampled_df.head(100)

artworks = []
seen_urls = set()

for _, row in sampled_df.iterrows():
    image_url = row['Link']
    if image_url in seen_urls:
        continue
    seen_urls.add(image_url)

    try:
        # Download and process the image
        response = requests.get(image_url, timeout=5)
        img = BytesIO(response.content)
        color_thief = ColorThief(img)

        dominant_color = color_thief.get_color(quality=1)
        palette = color_thief.get_palette(color_count=6)

        artwork = {
            "title": row["Artwork"],
            "artist": row["Artist"],
            "style": row["Style"],
            "image_url": image_url,
            "dominant_color": dominant_color,
            "palette": palette
        }
        artworks.append(artwork)

    except Exception as e:
        print(f"⚠️ Skipped '{row['Artwork']}' due to error: {e}")

# Save processed artworks with color data
with open("data/wikiart_stratify_processed.json", "w") as f:
    json.dump(artworks, f, indent=2)

# Also save the stratified raw data without color info (optional)
#sampled_df.to_json("data/wikiart_sampled_raw.json", orient="records", lines=True)

print(f"✅ Saved {len(artworks)} artworks with color palettes.")
