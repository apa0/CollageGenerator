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

# Function to calculate color distance (Euclidean distance in RGB space)
def color_distance(color1, color2):
    """Calculate Euclidean distance between two RGB colors"""
    r1, g1, b1 = hex_to_rgb(color1)
    r2, g2, b2 = hex_to_rgb(color2)
    return ((r1 - r2)**2 + (g1 - g2)**2 + (b1 - b2)**2) ** 0.5

# Function that uses weighted palette matching to find the best bucket
def get_closest_color_bucket_with_palette(dominant_color, color_palette, color_buckets):
    """
    Enhanced matching using the full color palette with weighted scoring
    - Dominant color: 70% weight (increased to prioritize it more)
    - Palette colors: 30% distributed across remaining colors (declining weights)
    
    This ensures dominant color has strong influence while still considering overall palette
    """
    min_score = float('inf')
    best_bucket = None
    best_bucket_color = None
    
    # Weight distribution: dominant gets 0.70, then 0.12, 0.09, 0.06, 0.03 for palette
    weights = [0.70, 0.12, 0.09, 0.06, 0.03]
    
    # Build color list: dominant + top palette colors (excluding dominant if it's in palette)
    track_colors = [dominant_color]
    for pal_color in color_palette[:5]:  # Take top 5 from palette
        if pal_color != dominant_color:  # Avoid duplicate
            track_colors.append(pal_color)
    
    # Normalize weights if we have fewer colors
    weights = weights[:len(track_colors)]
    weight_sum = sum(weights)
    weights = [w / weight_sum for w in weights]
    
    for bucket_key in color_buckets:
        try:
            bucket_color = parse_color_key(bucket_key)
            
            # Calculate weighted distance
            weighted_distance = 0.0
            for track_color, weight in zip(track_colors, weights):
                distance = color_distance(track_color, bucket_color)
                weighted_distance += distance * weight
            
            if weighted_distance < min_score:
                min_score = weighted_distance
                best_bucket = bucket_key
                best_bucket_color = bucket_color
                
        except ValueError:
            continue
    
    # Debug: print the selected bucket color
    if best_bucket_color:
        print(f"  → Matched bucket RGB: {best_bucket_color} (score: {min_score:.2f})")
    
    return best_bucket

#Function that uses Euclidean distance to find the best bucket match in WikiArt for a track
# Legacy function - kept for backward compatibility
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

# Function to get nearby color buckets when the primary bucket is exhausted
def get_nearby_color_buckets(target_color, color_buckets, max_distance=50, limit=5):
    """
    Returns a list of bucket keys sorted by distance from target_color
    Useful as fallback when primary bucket has no available artwork
    """
    r1, g1, b1 = hex_to_rgb(target_color)
    bucket_distances = []
    
    for bucket_key in color_buckets:
        try:
            r2, g2, b2 = parse_color_key(bucket_key)
            dist_sq = (r1 - r2)**2 + (g1 - g2)**2 + (b1 - b2)**2
            distance = dist_sq ** 0.5  # actual Euclidean distance
            
            if distance <= max_distance:
                bucket_distances.append((bucket_key, distance))
        except ValueError:
            continue
    
    # Sort by distance and return top N buckets
    bucket_distances.sort(key=lambda x: x[1])
    return [bucket for bucket, _ in bucket_distances[:limit]]

# Function to select unique artwork from a bucket, avoiding duplicates
def select_unique_artwork(bucket, used_artworks):
    """
    Selects a random artwork from bucket that hasn't been used yet
    Returns None if all artwork in bucket has been used
    """
    available_art = [art for art in bucket if art['image_url'] not in used_artworks]
    
    if available_art:
        return random.choice(available_art)
    return None

def match_images_to_tracks(user_tracks, bucket_file='Util/data/wikiart_expanded_color_buckets.json'):
    db = CollageCache()
    matched_tracks = []
    used_artworks = set()  # Track used artwork URLs to avoid duplicates
    
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
        
        # Only use cache if the artwork hasn't been used already
        if cached_artwork and cached_artwork not in used_artworks:
            print(" Using cached artwork (unique)")
            track['matched_artwork'] = cached_artwork
            used_artworks.add(cached_artwork)
            matched_tracks.append(track)
            continue
        elif cached_artwork and cached_artwork in used_artworks:
            print(" Cached artwork is duplicate, will find new match")
            # Don't use the duplicate, fall through to matching logic

        # If not in cache, perform matching
        print("No cache found, performing new match")
        dom_color = track['dominant_color']
        color_palette = track.get('color_palette', [])
        print(f"Dominant color: {dom_color}")
        print(f"Palette: {color_palette[:3]}...")  # Show first 3 colors
        
        # Try to find a unique artwork match using full palette
        matched_art = None
        best_bucket = get_closest_color_bucket_with_palette(dom_color, color_palette, color_buckets)
        print(f"Best color bucket (palette-matched): {best_bucket}")

        # First, try the best matching bucket
        if best_bucket and color_buckets[best_bucket]:
            matched_art = select_unique_artwork(color_buckets[best_bucket], used_artworks)
            if matched_art:
                print(f"✓ Selected unique artwork from best bucket: {matched_art['title']}")
            else:
                print("⚠ Best bucket exhausted, searching nearby buckets...")
                
                # Fallback: search nearby buckets
                nearby_buckets = get_nearby_color_buckets(dom_color, color_buckets, max_distance=80, limit=10)
                print(f"Found {len(nearby_buckets)} nearby buckets to search")
                
                for nearby_bucket in nearby_buckets:
                    if nearby_bucket != best_bucket and color_buckets[nearby_bucket]:
                        matched_art = select_unique_artwork(color_buckets[nearby_bucket], used_artworks)
                        if matched_art:
                            print(f" Selected artwork from nearby bucket: {matched_art['title']}")
                            break
        
        # If we found a match, store it
        if matched_art:
            image_url = matched_art['image_url']
            track['matched_artwork'] = image_url
            used_artworks.add(image_url)  # Mark as used
            print(f"Artwork URL: {image_url}")
            
            # Cache the match
            db.cache_wikiart_match(track['id'], image_url, 1.0)
            print("Cached the match")
        else:
            print(" No unique artwork found after searching all buckets")
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

