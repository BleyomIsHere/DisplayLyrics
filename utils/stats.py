import json
import os
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Any
import customtkinter as ctk
from utils.font_manager import FontManager
from utils.i18n import Translator
from dotenv import load_dotenv

load_dotenv()
lang_code = os.getenv("APP_LANG", "en")
t = Translator(lang_code).t


class MusicStats:
    def __init__(self, data_file: str = "data/music_stats.json"):
        self.data_file = data_file
        os.makedirs(os.path.dirname(data_file), exist_ok=True)
        self.data = self.load_data()
        self.current_track = None
        self.track_start_time = None

    def load_data(self) -> Dict[str, Any]:
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if "hours" in data:
                        hours = defaultdict(int)
                        hours.update(data["hours"])
                        data["hours"] = hours
                    for artist_data in data.get("artists", {}).values():
                        if isinstance(artist_data.get("unique_tracks"), list):
                            artist_data["unique_tracks"] = set(artist_data["unique_tracks"])
                    return data
            except Exception as e:
                print(f"[STATS] Error loading statistics: {e}")

        return {
            "tracks": {},
            "artists": {},
            "albums": {},
            "daily_activity": {},
            "hours": defaultdict(int),
            "total_listening_time": 0,
            "first_track": None,
            "last_updated": datetime.now().isoformat()
        }

    def save_data(self):
        try:
            data_to_save = dict(self.data)
            data_to_save["hours"] = dict(data_to_save["hours"])
            data_to_save["last_updated"] = datetime.now().isoformat()
            for artist, artist_data in data_to_save.get("artists", {}).items():
                if isinstance(artist_data.get("unique_tracks"), set):
                    artist_data["unique_tracks"] = list(artist_data["unique_tracks"])
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[STATS] Error saving statistics: {e}")

    def new_track(self, track_info: Dict[str, Any]):
        if self.current_track and self.track_start_time:
            listening_time = (datetime.now() - self.track_start_time).total_seconds() * 1000
            self.record_listening_time(self.current_track, int(listening_time))

        self.current_track = track_info
        self.track_start_time = datetime.now()

        if track_info:
            self.record_new_play(track_info)
            print(f"[STATS] New track: {track_info.get('title', 'Unknown')} - {track_info.get('artist', 'Unknown')}")
        else:
            print("[STATS] Track finalizado.")

    def record_new_play(self, track_info: Dict[str, Any]):
        if not track_info:
            return

        track_id = track_info.get("id", "")
        title = track_info.get("title", "Unknown")
        artist = track_info.get("artist", "Unknown")
        album = track_info.get("album", "Unknown")
        duration = track_info.get("duration", 0)

        if not self.data["first_track"]:
            self.data["first_track"] = {
                "title": title,
                "artist": artist,
                "date": datetime.now().isoformat()
            }

        if track_id not in self.data["tracks"]:
            self.data["tracks"][track_id] = {
                "title": title,
                "artist": artist,
                "album": album,
                "duration": duration,
                "plays": 0,
                "total_listening_time": 0,
                "first_played": datetime.now().isoformat(),
                "last_played": datetime.now().isoformat()
            }

        self.data["tracks"][track_id]["plays"] += 1
        self.data["tracks"][track_id]["last_played"] = datetime.now().isoformat()

        if artist not in self.data["artists"]:
            self.data["artists"][artist] = {
                "plays": 0,
                "total_time": 0,
                "unique_tracks": set()
            }

        if isinstance(self.data["artists"][artist]["unique_tracks"], list):
            self.data["artists"][artist]["unique_tracks"] = set(self.data["artists"][artist]["unique_tracks"])

        self.data["artists"][artist]["plays"] += 1
        self.data["artists"][artist]["unique_tracks"].add(track_id)

        if album not in self.data["albums"]:
            self.data["albums"][album] = {
                "artist": artist,
                "plays": 0,
                "total_time": 0
            }

        self.data["albums"][album]["plays"] += 1

        current_hour = datetime.now().hour
        self.data["hours"][current_hour] += 1

        self.save_data()

    def record_listening_time(self, track_info: Dict[str, Any], time_ms: int):
        if not track_info or time_ms <= 0:
            return

        track_id = track_info.get("id", "")
        artist = track_info.get("artist", "Unknown")
        album = track_info.get("album", "Unknown")

        if track_id in self.data["tracks"]:
            self.data["tracks"][track_id]["total_listening_time"] += time_ms

        if artist in self.data["artists"]:
            self.data["artists"][artist]["total_time"] += time_ms

        if album in self.data["albums"]:
            self.data["albums"][album]["total_time"] += time_ms

        today = datetime.now().date().isoformat()
        if today not in self.data["daily_activity"]:
            self.data["daily_activity"][today] = 0
        self.data["daily_activity"][today] += time_ms

        self.data["total_listening_time"] += time_ms

        print(f"[STATS] Recorded {time_ms/1000:.1f}s of {track_info.get('title', 'Unknown')}")
        self.save_data()

    def get_top_tracks(self, limit: int = 10) -> List[Dict[str, Any]]:
        sorted_tracks = sorted(
            self.data["tracks"].items(),
            key=lambda x: x[1]["plays"],
            reverse=True
        )
        return [
            {
                "title": data["title"],
                "artist": data["artist"],
                "plays": data["plays"],
                "total_time": self.format_time(data["total_listening_time"])
            }
            for _, data in sorted_tracks[:limit]
        ]

    def get_top_artists(self, limit: int = 10) -> List[Dict[str, Any]]:
        sorted_artists = sorted(
            self.data["artists"].items(),
            key=lambda x: x[1]["plays"],
            reverse=True
        )
        return [
            {
                "artist": artist,
                "plays": data["plays"],
                "total_time": self.format_time(data["total_time"]),
                "unique_tracks": len(data["unique_tracks"]) if isinstance(data["unique_tracks"], (list, set)) else 0
            }
            for artist, data in sorted_artists[:limit]
        ]

    def get_general_stats(self) -> Dict[str, Any]:
        total_tracks = len(self.data["tracks"])
        total_artists = len(self.data["artists"])
        total_plays = sum(t["plays"] for t in self.data["tracks"].values())
        total_time = self.data["total_listening_time"]
        favorite_hour = max(self.data["hours"].items(), key=lambda x: x[1]) if self.data["hours"] else (0, 0)

        return {
            "total_tracks": total_tracks,
            "total_artists": total_artists,
            "total_plays": total_plays,
            "total_time_formatted": self.format_time(total_time),
            "total_time_hours": total_time / 3600000,
            "favorite_hour": f"{int(favorite_hour[0]):02d}:00",
            "daily_average": self.calculate_daily_average()
        }

    def calculate_daily_average(self) -> str:
        if not self.data["daily_activity"]:
            return "0 min"

        days_with_activity = len(self.data["daily_activity"])
        total_time = sum(self.data["daily_activity"].values())
        average = total_time / days_with_activity if days_with_activity > 0 else 0

        return self.format_time(average)

    def format_time(self, milliseconds: int) -> str:
        if milliseconds < 1000:
            return t("less_than_1s")
        seconds = milliseconds // 1000
        minutes = seconds // 60
        hours = minutes // 60
        if hours > 0:
            return f"{hours}h {minutes % 60}m"
        elif minutes > 0:
            return f"{minutes}m {seconds % 60}s"
        else:
            return f"{seconds}s"


class StatsWindow:
    def __init__(self, parent_window, stats):
        self.stats = stats
        self.window = ctk.CTkToplevel(parent_window)
        self.window.title(t("stats_window_title"))
        self.window.geometry("900x700")
        self.window.configure(fg_color="#191414")

        self.fonts = FontManager()
        self.create_interface()
        self.update_data()

    def create_interface(self):
        self.summary_labels = {}

        title = ctk.CTkLabel(self.window, text=t("your_music_stats"),
                             font=self.fonts.get("Bold", 28), text_color="white")
        title.pack(pady=20)

        self.tabs = ctk.CTkTabview(self.window)
        self.tabs.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.summary_tab = self.tabs.add(t("summary_tab"))
        self.tracks_tab = self.tabs.add(t("tracks_tab"))
        self.artists_tab = self.tabs.add(t("artists_tab"))

        self.create_summary_tab()
        self.create_top_tracks_tab()
        self.create_top_artists_tab()

    def create_summary_tab(self):
        frame = ctk.CTkFrame(self.summary_tab, fg_color="#232323")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        stats = [
            ("total_tracks", t("unique_songs")),
            ("total_artists", t("unique_artists")),
            ("total_plays", t("total_plays")),
            ("total_time_formatted", t("total_time")),
            ("favorite_hour", t("favorite_hour")),
            ("daily_average", t("daily_average"))
        ]

        for i, (key, label) in enumerate(stats):
            stat_frame = ctk.CTkFrame(frame, fg_color="#2A2A2A", corner_radius=12)
            stat_frame.grid(row=i // 2, column=i % 2, padx=15, pady=15, sticky="nsew")

            ctk.CTkLabel(stat_frame, text=label, font=self.fonts.get("Regular", 18),
                         text_color="#b3b3b3").pack(pady=(5, 0))
            value_label = ctk.CTkLabel(stat_frame, text=t("loading"), font=self.fonts.get("SemiBold", 20),
                                       text_color="white")
            value_label.pack()
            self.summary_labels[key] = value_label

        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

    def create_top_tracks_tab(self):
        self.tracks_box = ctk.CTkScrollableFrame(self.tracks_tab, fg_color="#232323")
        self.tracks_box.pack(fill="both", expand=True, padx=20, pady=10)

    def create_top_artists_tab(self):
        self.artists_box = ctk.CTkScrollableFrame(self.artists_tab, fg_color="#232323")
        self.artists_box.pack(fill="both", expand=True, padx=20, pady=10)

    def update_data(self):
        stats = self.stats.get_general_stats()
        for key, label in self.summary_labels.items():
            label.configure(text=str(stats.get(key, "N/A")))

        for widget in self.tracks_box.winfo_children():
            widget.destroy()

        for i, track in enumerate(self.stats.get_top_tracks(25), 1):
            text = t("track_line").format(
                index=i,
                title=track["title"],
                artist=track["artist"],
                plays=track["plays"],
                total_time=track["total_time"]
            )
            ctk.CTkLabel(self.tracks_box, text=text, anchor="w", font=self.fonts.get("Regular", 18),
                         text_color="white").pack(anchor="w", padx=10, pady=4)

        for widget in self.artists_box.winfo_children():
            widget.destroy()

        for i, artist in enumerate(self.stats.get_top_artists(25), 1):
            text = t("artist_line").format(
                index=i,
                artist=artist["artist"],
                plays=artist["plays"],
                unique=artist["unique_tracks"],
                total_time=artist["total_time"]
            )
            ctk.CTkLabel(self.artists_box, text=text, anchor="w", font=self.fonts.get("Regular", 18),
                         text_color="white").pack(anchor="w", padx=10, pady=4)
