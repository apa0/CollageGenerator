#1. Need to load in data from JSON file
#4. Has algorithm to match recent track details to 6 photos from wiki art (this is the collage)
#5. Has a function to return the collage to the Controllers, which then passes it to the view...
#                                                   (which we dont have right now but thats fine)

import json
import random
import ast
from Model.collage_cache import CollageCache




# Update: Now that we know exactly what user data we are working with, we can clear up our approach to making matches

    # 1. Since our artwork dataset is set to expand, we want to narrow down our artwork pool first,
    # 2. We will do this by either genre to style tagging, or dominant color (if no genre)
                # For dominant color grouping, we can just round our RGB values to have a bit of a looser grouping and more possibility
    # 3. Once we have narrowed this down, we can use the top three colors in the pallete to give us the closest match
    # 4. Can later integrate better algorithms like KD-Trees or ANN (approximate nearest neighbors)

def parse_color_key(color_key):
    try:
        return ast.literal_eval(color_key)  # Turns "(0, 0, 0)" into (0, 0, 0)
    except Exception as e:
        raise ValueError(f"Invalid color bucket key format: {color_key}") from e


# Function that takes in the dominant color of a track and treat it as a point, hex to RGB integers
def hex_to_rgb(hexstr):
    if isinstance(hexstr, str) and hexstr.startswith('#') and len(hexstr) == 7:
        return tuple(int(hexstr[i:i+2], 16) for i in (1, 3, 5))
    elif isinstance(hexstr, (tuple, list)) and len(hexstr) == 3 and all(isinstance(c, int) for c in hexstr):
        return tuple(hexstr)  # Already an RGB triplet
    else:
        raise ValueError(f"Unexpected color format: {hexstr}")

#Function that uses Euclidean distance to find the best bucket match in WikiArt for a track
# Right now only using the dominant color to determine best bucket, later can incorporate pallates for specific image
def get_closest_color_bucket(track_color, color_buckets):
    r1, g1, b1 = hex_to_rgb(track_color)
    min_dist_sq = float('inf')
    best_bucket = None

    for bucket_key in color_buckets:
        try:
            r2, g2, b2 = parse_color_key(bucket_key)  # ✅ Safely convert string to tuple
        except ValueError as e:
            continue  # or log the error
        dist_sq = (r1 - r2)**2 + (g1 - g2)**2 + (b1 - b2)**2
        if dist_sq < min_dist_sq:
            min_dist_sq = dist_sq
            best_bucket = bucket_key
    return best_bucket

def match_images_to_tracks(user_tracks, bucket_file='Util/data/wikiart_stratify_color_buckets.json'):
    db = CollageCache()
    matched_tracks = []
    
    print("\n=== Starting match_images_to_tracks ===")
    print(f"Number of tracks to process: {len(user_tracks)}")
    
    # Load color buckets only once
    with open(bucket_file) as f:
        color_buckets = json.load(f)
        print(f"Loaded {len(color_buckets)} color buckets")

    for track in user_tracks:
        print(f"\nProcessing track: {track.get('name')}")
        print(f"Track ID: {track.get('id')}")
        
        # Check cache first
        cached_artwork = db.get_cached_wikiart_match(track['id'])
        print(f"Cache check result: {cached_artwork}")
        
        if cached_artwork:
            print("Using cached artwork")
            track['matched_artwork'] = cached_artwork
            matched_tracks.append(track)
            continue

        # If not in cache, perform matching
        print("No cache found, performing new match")
        dom_color = track['dominant_color']
        print(f"Dominant color: {dom_color}")
        
        best_bucket = get_closest_color_bucket(dom_color, color_buckets)
        print(f"Best color bucket: {best_bucket}")

        if best_bucket and color_buckets[best_bucket]:
            matched_art = random.choice(color_buckets[best_bucket])
            print(f"Selected artwork: {matched_art['title']}")
            print(f"Artwork URL: {matched_art['image_url']}")
            
            # Store ONLY the image URL
            image_url = matched_art['image_url']
            track['matched_artwork'] = image_url
            print(f"Stored URL in track: {track['matched_artwork']}")
            
            # Cache ONLY the image URL
            db.cache_wikiart_match(track['id'], image_url, 1.0)
            print("Cached the match")
        else:
            print("No matching artwork found")
            track['matched_artwork'] = None

        matched_tracks.append(track)

    print("\n=== Final matched tracks ===")
    for track in matched_tracks:
        print(f"\nTrack: {track.get('name')}")
        print(f"Matched artwork: {track.get('matched_artwork')}")
    
    return matched_tracks

# PLACEHOLDER: Now i need to take care of duplicate artwork being matched (do averages with top 3 pallete colors)
# I also want to later expand the size of the collage, aka right now we are only doing 10 artworks since we only take 10 tracks
# so we could add some logic to ask the person how far back we want to go in their listening history
# Also we could ask user if they want us to analyze their playlist, recent tracks, etc. give them options
# And of course, continue to expand on the dataset, instead of 100, go up to all of it!
# need to handle cases of SAME ALBUM??? randomness could help, but we want to maybe do something more meaningful
# Go by title?

#Can later add a function the allow user to save or download their image collage

