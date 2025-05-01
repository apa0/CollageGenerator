#2. This model needs to hold the user's data, right now thats just their recent tracks
#3. From the recent tracks we want to extract things like color, key words in titles, or genre...
#                                                   really it can get as complicated as we want

# Major problem: Spotify has deprecated their get_audio access from the API, so no energy, danceablity, etc.
# also deprecated the 30 sec preview of the track, so can't do some audio extraction there
# And i also tried to use an external API: reccobeats to no success
# BUT since we are focused on the track, we can work with the album cover for now
# And then we will try to incorporate / fix using an external api


import spotipy
import colorthief


class SpotifyUser:
    def __init__(self, token_info):
        self.token_info = token_info
        self.sp = spotipy.Spotify(auth=token_info['access_token'])
        self.recent_tracks = []

    #Limit 10 for now, testing
    def fetch_recent_tracks(self, limit=10):
        # Calls Spotify API to get recent tracks
        results = self.sp.current_user_recently_played(limit=limit)
        self.recent_tracks = [
            {
                'name' : item['track']['name'],
                'artist' : item['track']['artists'][0]['name'],
                'id' : item['track']['id'],
                'album_image_url' : item['track']['album']['images'][0]['url']
            }
            for item in results['items']
        ]
        return self.recent_tracks
