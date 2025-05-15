
from flask import session, redirect, url_for


from Model.user_data import SpotifyUser

#Helper function to instantiate SpotifyUser
def get_spotify_user():
    token_info = session.get("token_info", None)
    if not token_info:
        # let the routes determine what to do if Spotify user is None
        return redirect(url_for('index'))
    return SpotifyUser(token_info)
