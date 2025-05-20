from flask import Blueprint, render_template
import json

from Model.user_data import SpotifyUser
from Util.spotify_helper import get_spotify_user
from Util.user_collage import match_images_to_tracks


#This controller is in charge of creating the unique collage from unique user data

# Blueprint for /collage route
collage_bp = Blueprint('collage', __name__)

@collage_bp.route('/collage')
def collage():
    user = get_spotify_user()
    if isinstance(user, SpotifyUser):
        user_tracks = user.fetch_recent_tracks(limit=16)
        matched_tracks = match_images_to_tracks(user_tracks)
        
        # Debug printing
        print("\nDEBUG: Matched Tracks Data:")
        for track in matched_tracks:
            print(f"Track: {track.get('name')}")
            print(f"Matched Artwork: {json.dumps(track.get('matched_artwork'), indent=2)}")
            print("---")
            
        return render_template("collage.html", matched_tracks=matched_tracks)

    return user