import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

load_dotenv()

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
    scope="user-read-playback-state user-modify-playback-state user-read-currently-playing"
))

def get_current_playing_track():
    try:
        playback = sp.current_playback()
        if playback and playback.get("item"):
            item = playback["item"]
            return {
                "id": item["id"],
                "title": item["name"],
                "artist": item["artists"][0]["name"],
                "album": item["album"]["name"],
                "duration": item["duration_ms"],
                "progress_ms": playback["progress_ms"],
                "album_image_url": item["album"]["images"][0]["url"]
            }
        else:
            print("[Spotify] Nada está sonando.")
    except Exception as e:
        print(f"[Spotify] Error al obtener canción: {e}")
    return None
