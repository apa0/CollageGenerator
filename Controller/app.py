from flask import Flask, request, redirect, session, url_for, render_template
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

from Controller.configure import scope
from Util.user_collage import match_images_to_tracks
from Model.user_data import SpotifyUser

load_dotenv()


# This file acts similar to a controller in MVC
# handles the logic, routes and user interactions
#Since we don't really have a UI right now, our events are URL visits instead of widgets



# Setting up the app
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

#Helper function to instantiate SpotifyUser
def get_spotify_user():
    token_info = session.get("token_info", None)
    if not token_info:
        # let the routes determine what to do if Spotify user is None
        return redirect(url_for('index'))
    return SpotifyUser(token_info)

#Handles authentication, when the user initially visits the URL
@app.route('/')
def index():
    sp_oauth = SpotifyOAuth(scope=scope)
    auth_url = sp_oauth.get_authorize_url()
    return render_template("homepage.html", auth_url=auth_url)

#Handles the result of a redirect from Spotify --> right now its after the authentication
@app.route('/callback')
def callback():
    #Sets up SpotifyOAuth object and cleans prev saved info
    sp_oauth = SpotifyOAuth(scope=scope)
    session.clear()
    #Authorization code when user logged in
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    #Saving access token
    session["token_info"] = token_info
    #User redirected to /recent
    return redirect(url_for('recent_tracks'))

#Grabbing recent listened to tracks from Spotify
@app.route('/recent')
def recent_tracks():
    user = get_spotify_user()
    if isinstance(user, SpotifyUser):
        recent_music = user.fetch_recent_tracks(limit=16)
        return render_template('recent_tracks.html', recent_music=recent_music)
    #Redirect
    return user

@app.route('/collage')
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



if __name__ == '__main__':
    app.run(debug=True, port=5001)