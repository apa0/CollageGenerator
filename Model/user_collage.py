#1. Need to load in data from JSON file
#4. Has algorithm to match recent track details to 6 photos from wiki art (this is the collage)
#5. Has a function to return the collage to the Controller, which then passes it to the view...
#                                                   (which we dont have right now but thats fine)

import json
import random
from Util.color_buckets import color_buckets



# Update: Now that we know exactly what user data we are working with, we can clear up our approach to making matches

    # 1. Since our artwork dataset is set to expand, we want to narrow down our artwork pool first,
    # 2. We will do this by either genre to style tagging, or dominant color (if no genre)
                # For dominant color grouping, we can just round our RGB values to have a bit of a looser grouping and more possibility
    # 3. Once we have narrowed this down, we can use the top three colors in the pallete to give us the closest match
    # 4. Can later integrate better algorithms like KD-Trees or ANN (approximate nearest neighbors)


# Function that takes in the dominant color of a track and treat it as a point, hex to RGB integers
def hex_to_rgb(hexstr):
    return tuple(int(hexstr[i:i+2], 16) for i in (1,3,5))

#Function that uses Euclidean distance to find the best bucket match in WikiArt for a track
# Right now only using the dominant color to determine best bucket, later can incorporate pallates for specific image
def get_closest_color_bucket(track_color, color_buckets):
    r1, g1, b1 = hex_to_rgb(track_color)
    min_dist_sq = float('inf')
    best_bucket = None

    for bucket_hex in color_buckets:
        r2, g2, b2 = hex_to_rgb(bucket_hex)
        dist_sq = (r1 - r2)**2 + (g1 - g2)**2 + (b1 - b2)**2
        if dist_sq < min_dist_sq:
            min_dist_sq = dist_sq
            best_bucket = bucket_hex
    return best_bucket

def match_images_to_tracks(user_tracks, bucket_file='Util/data/wikiart_color_buckets.json'):
    with open(bucket_file) as f:
        color_buckets = json.load(f)

    matched_tracks = []
    for track in user_tracks:
        # Check format here to match: '#RRGGBB'
        dom_color=track['dominant_color']
        best_bucket = get_closest_color_bucket(dom_color, color_buckets)
        if best_bucket and color_buckets[best_bucket]:
            # Right now, I am picking a random art work out of the best bucket
            # Come back to instead call another helper function that does Eulerian distance
            # By looping through and averaging the top 3 palletes to find best match
            matched_art=random.choice(color_buckets[best_bucket])
        else: # If nothing was found
            track['matched_artwork'] = None
        matched_tracks.append(track)
    return matched_tracks

def generate_collage_html(matched_tracks):
    html = "<h2>Track-to-Art Collage</h2>"
    for track in matched_tracks:
        html += f"""
            <div style='margin-bottom: 30px;'>
                <img src="{track['album_image_url']}" style="width: 100px;'><br>
                <strong>{track['name']}</strong> by {track['artist']}<br>
                Dominant Color: <div style='width: 20px; height: 20px; background-color: {track['dominant_color']}; display: inline-block;'></div> {track['dominant_color']}<br>
        """
        if 'matched_artwork' in track and track['matched_artwork']:
            html += f"""
                Matched Artwork:<br>
                <img src="{track['matched_artwork']}" style="width: 150px;'><br>
            """
        else:
            html += "No artwork matched.<br>"

        html += "<div style='margin-top: 10px;'>Palette:<br>"
        for color in track['color_palette']:
            html += f"<div style='width: 20px; height: 20px; background-color: {color}; display: inline-block; margin-right: 5px;'></div>"
        html += "</div></div>"

    return html

#Can later add a function the allow user to save or download their image collage

