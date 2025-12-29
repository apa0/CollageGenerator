
from flask import session, redirect, url_for
import time

from Model.user_data import SpotifyUser
from Controllers.auth_controller import get_spotify_oauth

#Helper function to instantiate SpotifyUser with token refresh
def get_spotify_user():
    token_info = session.get("token_info", None)
    if not token_info:
        # let the routes determine what to do if Spotify user is None
        return redirect(url_for('auth.index'))
    
    # Check if token is expiring soon and refresh if needed
    now = int(time.time())
    should_refresh = token_info.get('expires_at', 0) < now + 60  # Refresh if expires in less than 60 seconds
    
    if should_refresh:
        refresh_token = token_info.get('refresh_token')
        if not refresh_token:
            # No refresh token available; treat as unauthenticated and let routes handle re-auth
            return redirect(url_for('auth.index'))

        sp_oauth = get_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(refresh_token)
        session['token_info'] = token_info
    
    return SpotifyUser(token_info)
