import pandas as pd
import requests
import json
from io import BytesIO
from colorthief import ColorThief
from collections import defaultdict
import time

# Enhanced preprocessing: Expand to 500-1000 artworks with better color diversity
# Strategy: Sample 10-15 artworks per style (instead of 3), ensuring color variety

print("=== Expanding WikiArt Dataset ===\n")

# Load the CSV file
print("Loading CSV...")
df = pd.read_csv("../data/wikiart_scraped.csv")
df.columns = df.columns.str.strip()

# Drop rows without image links
df = df.dropna(subset=['Link'])
print(f"Total artworks available: {len(df)}")
print(f"Unique styles: {df['Style'].nunique()}\n")

# Group by style and sample 10 artworks per style (more diversity)
print("Sampling artworks by style...")
grouped = df.groupby('Style')
sampled_df = grouped.apply(lambda x: x.sample(n=min(10, len(x)), random_state=42)).reset_index(drop=True)

# Remove duplicate image URLs
sampled_df = sampled_df.drop_duplicates(subset=['Link'])

# Target 500 artworks (can adjust)
TARGET_SIZE = 500
sampled_df = sampled_df.head(TARGET_SIZE)

print(f"Processing {len(sampled_df)} artworks...")
print("This may take several minutes...\n")

artworks = []
seen_urls = set()
failed_count = 0

for idx, row in sampled_df.iterrows():
    image_url = row['Link']
    if image_url in seen_urls:
        continue
    seen_urls.add(image_url)

    try:
        # Download and process the image
        response = requests.get(image_url, timeout=10)
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
        
        # Progress indicator
        if (idx + 1) % 50 == 0:
            print(f"Processed {idx + 1}/{len(sampled_df)} artworks ({len(artworks)} successful)")

    except Exception as e:
        failed_count += 1
        if failed_count <= 5:  # Only print first 5 errors
            print(f"⚠ Failed to process {row['Artwork']}: {e}")
        continue
    
    # Small delay to avoid overwhelming servers
    time.sleep(0.1)

print(f"\n✓ Successfully processed {len(artworks)} artworks")
print(f"✗ Failed to process {failed_count} artworks")

# Save processed artworks
output_file = "../data/wikiart_expanded_processed.json"
with open(output_file, 'w') as f:
    json.dump(artworks, f, indent=2)
print(f"\n✓ Saved to {output_file}")

# Create color buckets (round to nearest 40 for good bucket sizes)
print("\nCreating color buckets...")
color_buckets = defaultdict(list)

for artwork in artworks:
    r, g, b = artwork['dominant_color']
    # Round to nearest 40 for good distribution
    bucket_key = (round(r / 40) * 40, round(g / 40) * 40, round(b / 40) * 40)
    color_buckets[str(bucket_key)].append(artwork)

print(f"✓ Created {len(color_buckets)} color buckets")
print(f"✓ Average artworks per bucket: {len(artworks) / len(color_buckets):.1f}")

# Save color buckets
bucket_output = "../data/wikiart_expanded_color_buckets.json"
with open(bucket_output, 'w') as f:
    json.dump(color_buckets, f, indent=2)
print(f"✓ Saved color buckets to {bucket_output}")

# Print color distribution
print("\n=== Color Distribution ===")
sorted_buckets = sorted(color_buckets.items(), key=lambda x: len(x[1]), reverse=True)
print("Top 10 most common color buckets:")
for bucket_key, artwork_list in sorted_buckets[:10]:
    r, g, b = eval(bucket_key)
    print(f"  RGB({r:3d}, {g:3d}, {b:3d}) → {len(artwork_list)} artworks")

print("\n✅ Dataset expansion complete!")
print(f"To use this dataset, update user_collage.py to use:")
print(f"  bucket_file='Util/data/wikiart_expanded_color_buckets.json'")
