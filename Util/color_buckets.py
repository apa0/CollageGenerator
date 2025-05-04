import json
from collections import defaultdict

#Primary goal: we can minimize match time later by storing our wiki art data into color buckets
# That way we can use the dominant color of the track first to narrow down the art pool dramatically (hopefully)
# And then, we can use more specific metadata like top 3 pallete colors, and genre to style, to get the best match
# While still being efficient (hopefully)


# To avoid having lopsided buckets, we "quantize" dominant colors
# This groups similar shades into the same bucket (e.g., multiple reds or blues), increasing match potential
def quantize_color(color, step=40):
    return tuple((c // step) * step for c in color)


# Load processed artwork data
with open("data/wikiart_processed.json", "r") as f:
    artworks = json.load(f)

# Initialize the hashmap: keys are dominant colors (as strings for JSON compatibility), values are lists of artworks
color_buckets = defaultdict(list)

# Fill the hashmap
for art in artworks:
    dominant_color = quantize_color(tuple(art["dominant_color"]), step=40) # Ensure tuple format for hashing
    palette = art.get("palette", [])[:3]  # Take only the top 3 colors, this is what we will be searching by after

    # Build the minimal representation for matching (losing metadata for the sake of memory in hashmap)
    entry = {
        "image_url": art["image_url"],
        "style": art["style"],
        "title": art["title"],
        "palette": palette
    }

    color_buckets[str(dominant_color)].append(entry)  # Store with stringified color as key

# Save the hashmap to a new JSON file
with open("data/wikiart_color_buckets.json", "w") as f:
    json.dump(color_buckets, f, indent=2)

print("✅ Hashmap of artworks bucketed by dominant color has been saved.")


# Summary: Show how many artworks are in each bucket
bucket_sizes = {k: len(v) for k, v in color_buckets.items()}
sorted_buckets = sorted(bucket_sizes.items(), key=lambda x: x[1], reverse=True)

# Print top 10 buckets with most artworks
print("\n🎨 Top 10 most populated color buckets:")
for color, count in sorted_buckets[:10]:
    print(f"{color}: {count} artworks")

print(f"\n📦 Total buckets: {len(bucket_sizes)}")
print(f"🖼️ Total artworks processed: {sum(bucket_sizes.values())}")

# Plot distribution (requires matplotlib)
try:
    import matplotlib.pyplot as plt

    plt.figure(figsize=(12, 6))
    plt.hist(bucket_sizes.values(), bins=range(1, max(bucket_sizes.values()) + 2), edgecolor='black')
    plt.title("Distribution of Artworks per Color Bucket")
    plt.xlabel("Number of Artworks in Bucket")
    plt.ylabel("Number of Buckets")
    plt.grid(True)
    plt.tight_layout()
    plt.show()
except ImportError:
    print("\n📉 matplotlib not installed — skipping histogram. Install it with 'pip install matplotlib' if you want charts.")