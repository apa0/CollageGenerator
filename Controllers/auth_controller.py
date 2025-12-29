from flask import Blueprint, session, redirect, request, url_for, render_template
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os


#This controller is responsible for the inital authentication into Spotify API
# Redirects to recent tracks route automatically (could change)

from Controllers.configure import scope

load_dotenv()

auth_bp = Blueprint("auth", __name__)

def get_spotify_oauth():
    """
    Create and return a configured SpotifyOAuth instance.

    This factory function reads Spotify credentials and redirect URI from
    environment variables (``SPOTIPY_CLIENT_ID``, ``SPOTIPY_CLIENT_SECRET``,
    and ``SPOTIPY_REDIRECT_URI``) and uses the globally imported ``scope``
    from ``Controllers.configure`` to configure the authorization scopes.

    Returns:
        spotipy.oauth2.SpotifyOAuth: A SpotifyOAuth client configured with
        environment-based credentials and the global authorization scope.
    
    Raises:
        ValueError: If any required environment variable is missing.
    """
    client_id = os.getenv("SPOTIPY_CLIENT_ID")
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
    redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")
    
    required = {
        "SPOTIPY_CLIENT_ID": client_id,
        "SPOTIPY_CLIENT_SECRET": client_secret,
        "SPOTIPY_REDIRECT_URI": redirect_uri,
    }
    missing = [name for name, value in required.items() if not value]
    
    if missing:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}. "
            "Please check your .env file."
        )
    
    return SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=scope
    )

@auth_bp.route('/')
def index():
    sp_oauth = get_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return render_template("homepage.html", auth_url=auth_url)

@auth_bp.route('/callback')
def callback():
    sp_oauth = get_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session["token_info"] = token_info
    return redirect(url_for('recent.recent_tracks'))  # Update based on blueprint naming