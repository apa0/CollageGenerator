from flask import Blueprint, session, redirect, request, url_for, render_template
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv


#This controller is responsible for the inital authentication into Spotify API
# Redirects to recent tracks route automatically (could change)

from Controllers.configure import scope

load_dotenv()

auth_bp = Blueprint("auth", __name__)

@auth_bp.route('/')
def index():
    sp_oauth = SpotifyOAuth(scope=scope)
    auth_url = sp_oauth.get_authorize_url()
    return render_template("homepage.html", auth_url=auth_url)

@auth_bp.route('/callback')
def callback():
    sp_oauth = SpotifyOAuth(scope=scope)
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session["token_info"] = token_info
    return redirect(url_for('recent.recent_tracks'))  # Update based on blueprint naming