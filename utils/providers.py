import requests
import urllib.parse
import re

def parse_lrc(lrc_text):
    pattern = re.compile(r"\[(\d+):(\d+)(?:\.(\d+))?\](.*)")
    parsed = []

    for line in lrc_text.splitlines():
        match = pattern.match(line)
        if match:
            minutes = int(match.group(1))
            seconds = int(match.group(2))
            milliseconds = int(match.group(3) or 0)
            total_seconds = minutes * 60 + seconds + milliseconds / 1000
            text = match.group(4).strip()
            if text:
                parsed.append({"time": total_seconds, "line": text})
    return parsed

def provider_lrclib(info):
    track_name = info.get("title", "")
    artist_name = info.get("artist", "")
    album_name = info.get("album", "")
    duration_ms = int(info.get("duration", 0))
    duration = duration_ms // 1000

    # URL encode
    encoded_track_name = urllib.parse.quote(track_name)
    encoded_artist_name = urllib.parse.quote(artist_name)
    encoded_album_name = urllib.parse.quote(album_name)

    url = (
        f"https://lrclib.net/api/get"
        f"?track_name={encoded_track_name}"
        f"&artist_name={encoded_artist_name}"
        f"&album_name={encoded_album_name}"
        f"&duration={duration}"
    )

    headers = {
        "User-Agent": "DisplayLyrics/1.0 (https://github.com/BleyomIsHere/DisplayLyrics)"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data.get("syncedLyrics"):
            print("[LRCLIB] Synced Lyrics found.")
            parsed = parse_lrc(data["syncedLyrics"])
            return {
                "provider": "lrclib",
                "synced": True,
                "lyrics": parsed,
                "status": "found"
            }
        elif data.get("plainLyrics"):
            print("[LRCLIB] Synced lyrics not found.")
            return {
                "provider": "lrclib",
                "synced": False,
                "lyrics": data["plainLyrics"],
                "status": "not_found"
            }

    print(f"[LRCLIB] Lyrics not found (status {response.status_code}).")
    return {
        "provider": "lrclib",
        "synced": False,
        "lyrics": [],
        "status": "not_found"
    }

__all__ = ["provider_lrclib"]
