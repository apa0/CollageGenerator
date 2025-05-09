from re import match

from flask import Flask, request, redirect, session, url_for
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

from Controller.configure import scope
from Model.user_collage import match_images_to_tracks, generate_collage_html
from Model.user_data import SpotifyUser

load_dotenv()


# This file acts similar to a controller in MVC
# handles the logic, routes and user interactions
#Since we don't really have a UI right now, our events are URL visits instead of widgets



# Setting up the app
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")



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

    #TESTING NEW LOGIC TO GATHER USER DATA:
    user = SpotifyUser(token_info)
    recent_music = user.fetch_recent_tracks(limit=10)



    # Build a simple HTML display of track info + colors
    html = "<h2>Recent Tracks with Color Analysis</h2>"
    for track in recent_music:
        html += f"""
                <div style='margin-bottom: 30px;'>
                    <img src="{track['album_image_url']}" style="width: 100px;"><br>
                    <strong>{track['name']}</strong> by {track['artist']}<br>
                    Genre: {track['genres']}<br>  <!-- Display genre here -->
                    Dominant Color: <div style='width: 20px; height: 20px; background-color: rgb{track['dominant_color']}; display: inline-block;'></div> {track['dominant_color']}<br>
                    Color Palette:<br>
            """
        for color in track['color_palette']:
            html += f"<div style='width: 20px; height: 20px; background-color: rgb{color}; display: inline-block; margin-right: 5px;'></div>"
        html += "</div>"

        html += """
            <form action="/collage" method="get">
                <button type="submit" style="padding: 10px 20px; font-size: 16px;">🎨 Generate Collage</button>
            </form>
        """

    return html

@app.route('/collage')
def collage():

    token_info = session.get("token_info", None)
    if not token_info:
        return redirect(url_for('index'))
    user = SpotifyUser(token_info)
    user_tracks = user.fetch_recent_tracks(limit=10)
    matched_tracks = match_images_to_tracks(user_tracks)
    collage_html=generate_collage_html(matched_tracks)

    return collage_html


    #sp = spotipy.Spotify(auth=token_info['access_token'])
    #results = sp.current_user_recently_played(limit=40)
    #tracks = []
    #for item in results['items']:
     #   track = item['track']
      #  tracks.append(f"{track['name']} by {track['artists'][0]['name']}")

    #return "<br>".join(tracks)


#Will need a /collage where we generate and show the image collage 


if __name__ == '__main__':
    app.run(debug=True, port=5001)