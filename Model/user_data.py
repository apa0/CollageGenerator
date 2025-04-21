#2. This model needs to hold the user's data, right now thats just their recent tracks
#3. From the recent tracks we want to extract things like color, key words in titles, or genre...
#                                                   really it can get as complicated as we want
class SpotifyUser:
    def __init__(self, token_info):
        self.token_info = token_info
        self.recent_tracks = []

    def fetch_recent_tracks(self):
        # call Spotify API and fill self.recent_tracks
        pass

    def extract_features(self):
        # pull genres, keywords, or colors, etc.
        return {
            'genres': [],
            'keywords': [],
            'colors': []
        }