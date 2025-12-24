from flask import Blueprint, render_template, request

from Model.user_data import SpotifyUser
from Util.spotify_helper import get_spotify_user

#This controller is responsible for generating the color analysis for the user's recent tracks,
# prompts the user to generate their collage

# Blueprint for /recent route
recent_bp = Blueprint('recent', __name__)

@recent_bp.route('/recent')
def recent_tracks():
    user = get_spotify_user()
    if not isinstance(user, SpotifyUser):
        return user
    # user was redirected due to invalid session

    # Check if user requested a refresh
    force_refresh = request.args.get('refresh', 'false').lower() == 'true'
    recent_music = user.fetch_recent_tracks(force_refresh=force_refresh)
    
    # Debug printing
    print("\nDEBUG: Recent Tracks Data:")
    for track in recent_music:
        print(f"\nTrack: {track.get('name')}")
        print(f"Dominant Color: {track.get('dominant_color')}")
        print(f"Color Palette: {track.get('color_palette')}")
        print("---")
    
    return render_template("recent_tracks.html", recent_music=recent_music)

