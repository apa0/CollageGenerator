#2. This model needs to hold the user's data, right now thats just their recent tracks
#3. From the recent tracks we want to extract things like color, key words in titles, or genre...
#                                                   really it can get as complicated as we want
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests

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

    #Function to use Reccobeats API, following docs
    def get_features_for_track(self, track_id):
        url = "https://api.reccobeats.com/v1/analysis/audio-features"
        payload = {
            'track_id' : track_id
        }
        headers = {
            'Accept' : 'application/json'
        }
        try:
            response = requests.post(url, headers=headers, data=payload)
            # This will raise an error for non-200 responses
            response.raise_for_status()
            # Parse JSON response
            data=response.json()
            return {
                "valence" : data.get("valence"),
                "energy" : data.get("energy")
            }

        except requests.exceptions.RequestException as e:
            print(f"Error fetching features for track {track_id}: {e}")
            return None
        except ValueError as e:
            print(f"Error parsing JSON for track {track_id}: {e}")
            return None



    #Function to store valence and energy feature from selected track
    #Spotify API audio_features is deprecated, so using alternative Reccobeats
    #Focusing on valence and energy for best, specialized data for collage:
    # If you want to learn more about other fields: https://reccobeats.com/docs/apis/extract-audio-features
    def fetch_audio_features(self):
        for track in self.recent_tracks:
            track_id = track.get("id")
            if not track_id:
                continue
            features = self.get_features_for_track(track['id'])
            if features: # Update track with fetched fetures
                track.update(features)