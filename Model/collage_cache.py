import sqlite3
from datetime import datetime, timedelta
import json
from typing import List, Dict, Optional

class CollageCache:
    """
    Handles caching of Spotify track data and WikiArt matches for the collage generator
    Uses SQLite to persist data between sessions and reduce API calls
    """
    def __init__(self, db_path: str = 'collage_cache.db'):
        self.db_path = db_path
        self.init_db()


    """
    Initializes the SQLite database with two tables:
    - user_tracks: Stores Spotify track data including color analysis
    - wikiart_matches: Stores the matched WikiArt pieces for each track
    """
    def init_db(self):
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_tracks (
                    user_id TEXT,
                    track_id TEXT,
                    track_name TEXT,
                    artist_name TEXT,
                    album_image_url TEXT,
                    genres TEXT,
                    dominant_color TEXT,
                    color_palette TEXT,
                    last_updated TIMESTAMP,
                    PRIMARY KEY (user_id, track_id)
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS wikiart_matches (
                    track_id TEXT,
                    artwork_url TEXT,
                    match_score REAL,
                    timestamp TEXT,
                    PRIMARY KEY (track_id)
                )
            ''')
    
    """
    Caches a user's Spotify tracks and their associated data
    Stores track metadata, album cover colors, and genres
    Each track is uniquely identified by user_id and track_id
    
    Args:
        user_id: Spotify user ID
        tracks: List of track dictionaries containing track data and color analysis
        """
    def cache_tracks(self, user_id: str, tracks: List[Dict]):

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            now = datetime.now()
            
            for track in tracks:
                # Ensure all data is properly serialized
                track_data = {
                    'id': str(track['id']),
                    'name': str(track['name']),
                    'artist': str(track['artist']),
                    'album_image_url': str(track['album_image_url']),
                    'genres': json.dumps(track['genres']),
                    'dominant_color': json.dumps(track['dominant_color']),
                    'color_palette': json.dumps(track['color_palette'])
                }
                
                cursor.execute('''
                    INSERT OR REPLACE INTO user_tracks 
                    (user_id, track_id, track_name, artist_name, album_image_url, 
                     genres, dominant_color, color_palette, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    str(user_id),
                    track_data['id'],
                    track_data['name'],
                    track_data['artist'],
                    track_data['album_image_url'],
                    track_data['genres'],
                    track_data['dominant_color'],
                    track_data['color_palette'],
                    now
                ))


    """
    Retrieves cached tracks for a user if they exist and are not expired
    Returns None if no valid cache exists
    
    Args:
        user_id: Spotify user ID
        max_age_hours: Maximum age of cache in hours (default: 24)
        
    Returns:
        List of track dictionaries or None if cache is expired/missing
    """
    def get_cached_tracks(self, user_id: str, max_age_hours: int = 24) -> Optional[List[Dict]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            
            cursor.execute('''
                SELECT * FROM user_tracks 
                WHERE user_id = ? AND last_updated > ?
                ORDER BY last_updated DESC
            ''', (user_id, cutoff_time))
            
            rows = cursor.fetchall()
            if not rows:
                return None
                
            tracks = []
            for row in rows:
                track = {
                    'id': row[1],
                    'name': row[2],
                    'artist': row[3],
                    'album_image_url': row[4],
                    'genres': json.loads(row[5]),
                    'dominant_color': json.loads(row[6]),
                    'color_palette': json.loads(row[7])
                }
                tracks.append(track)
            return tracks


    """
    Caches a WikiArt piece that was matched to a Spotify track
    Stores the match with a score indicating how well it matches the track's colors
    
    Args:
        track_id: Spotify track ID
        artwork_url: URL of the matched WikiArt piece
        match_score: Score indicating match quality (0.0 to 1.0)
    """
    def cache_wikiart_match(self, track_id, artwork_url, match_score):
        """Cache a WikiArt match for a track"""
        try:
            # Convert track_id to string to ensure compatibility
            track_id = str(track_id)
            artwork_url = str(artwork_url)
            match_score = float(match_score)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO wikiart_matches 
                    (track_id, artwork_url, match_score, timestamp) 
                    VALUES (?, ?, ?, ?)
                ''', (track_id, artwork_url, match_score, datetime.now().isoformat()))
                
                conn.commit()
            
        except Exception as e:
            print(f"Error caching WikiArt match: {e}")
            with sqlite3.connect(self.db_path) as conn:
                conn.rollback()
   
    """
    Retrieves a cached WikiArt match for a track if it exists and is not expired
    Returns None if no valid cache exists
    
    Args:
        track_id: Spotify track ID
        max_age_hours: Maximum age of cache in hours (default: 24)
        
    Returns:
        URL of the matched WikiArt piece or None if cache is expired/missing
    """
    def get_cached_wikiart_match(self, track_id, max_age_hours=24):
        """Get cached WikiArt match for a track if it exists and is not too old"""
        try:
            # Convert track_id to string to ensure compatibility
            track_id = str(track_id)
            
            # Get the cached match
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT artwork_url, match_score, timestamp 
                    FROM wikiart_matches 
                    WHERE track_id = ?
                ''', (track_id,))
                
                result = cursor.fetchone()
                if result:
                    artwork_url, match_score, timestamp = result
                    
                    # Check if the cache is still valid
                    if timestamp and (datetime.now() - datetime.fromisoformat(timestamp)).total_seconds() < max_age_hours * 3600:
                        return artwork_url  # Return just the URL
            return None
            
        except Exception as e:
            print(f"Error getting cached WikiArt match: {e}")
            return None