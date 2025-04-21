from flask import Flask, request, redirect, session, url_for
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
load_dotenv()


# This file acts similar to a controller in MVC
# handles the logic, routes and user interactions
#Since we don't really have a UI right now, our events are URL visits instead of widgets



# Setting up the app
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

#Currently fetching recently played tracks (could add user-library-read" or "user-top-read"
scope = "user-read-recently-played"

#Handles authentication, when the user initially visits the URL
@app.route('/')
def index():
    sp_oauth = SpotifyOAuth(scope=scope)
    auth_url = sp_oauth.get_authorize_url()
    return f'<a href="{auth_url}">Login with Spotify</a>'

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
    token_info = session.get("token_info", None)
    if not token_info:
        return redirect(url_for('index'))

    sp = spotipy.Spotify(auth=token_info['access_token'])
    results = sp.current_user_recently_played(limit=40)
    tracks = []
    for item in results['items']:
        track = item['track']
        tracks.append(f"{track['name']} by {track['artists'][0]['name']}")

    return "<br>".join(tracks)


#Will need a /collage where we generate and show the image collage 


if __name__ == '__main__':
    app.run(debug=True, port=5001)