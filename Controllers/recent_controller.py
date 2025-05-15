from flask import Blueprint, render_template

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


    recent_music = user.fetch_recent_tracks()
    return render_template("recent_tracks.html", recent_music=recent_music)

