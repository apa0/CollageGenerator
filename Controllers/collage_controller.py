
from flask import Blueprint, render_template

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
    # Debugging: print matched artwork URLs
        for i, track in enumerate(matched_tracks):
            print(f"Track {i}: {track.get('name', 'N/A')} - matched_artwork: {track.get('matched_artwork')}")
        return render_template("collage.html", matched_tracks=matched_tracks)

    return user