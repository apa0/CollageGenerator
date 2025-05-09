#2. This model needs to hold the user's data, right now thats just their recent tracks
#3. From the recent tracks we want to extract things like color, key words in titles, or genre...
#                                                   really it can get as complicated as we want
from io import BytesIO

import requests
# Major problem: Spotify has deprecated their get_audio access from the API, so no energy, danceablity, etc.
# also deprecated the 30 sec preview of the track, so can't do some audio extraction there
# And i also tried to use an external API: reccobeats to no success
# BUT since we are focused on the track, we can work with the album cover for now
# And then we will try to incorporate / fix using an external api


import spotipy
from colorthief import ColorThief




class SpotifyUser:
    def __init__(self, token_info):
        self.token_info = token_info
        self.sp = spotipy.Spotify(auth=token_info['access_token'])
        self.recent_tracks = self.fetch_recent_tracks()

    #Limit 10 for now, testing
    def fetch_recent_tracks(self, limit=10):
        #Calling Spotify API to get recent tracks
        results = self.sp.current_user_recently_played(limit=limit)
        self.recent_tracks = []

        for item in results['items']:
            track = item['track']
            artist = track['artists'][0]
            artist_id = artist['id']
            artist_name = artist['name']

            # Fetch genre info using artist ID, right now only taking in one genre (most relevant)
            artist_info = self.sp.artist(artist_id)
            genres = artist_info.get('genres', [])


            # If genres is empty or None, set it to 'Unknown'
            if not genres:
                genres = ['Unknown']

            self.recent_tracks.append({
                'name': track['name'],
                'artist': artist_name,
                'id': track['id'],
                'album_image_url': track['album']['images'][0]['url'],
                'genres': genres[0]
            })
        # Call helper function to append color analysis of album cover
        self.fetch_color_analysis()

        return self.recent_tracks


    # Potential looking into: using library like colormath to infer mood of the song using color theory of album
    def fetch_color_analysis(self):
        for track in self.recent_tracks:
            album_cover = requests.get(track['album_image_url'])
            img = BytesIO(album_cover.content)
            color_thief = ColorThief(img)

            #Extract colors
            dominant_color = color_thief.get_color(quality=10)
            palette = color_thief.get_palette(color_count=6)

            #Add these new fields to user_data
            track['dominant_color'] = dominant_color
            track['color_palette'] = palette

