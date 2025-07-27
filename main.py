import os
import time
import requests
from PIL import Image, ImageDraw
from io import BytesIO
from dotenv import load_dotenv
import customtkinter as ctk
from customtkinter import CTkImage

from utils.providers import provider_lrclib
from utils.spotify import get_current_playing_track, sp
from utils.stats import MusicStats, StatsWindow
from utils.font_manager import FontManager
from utils.i18n import Translator

def load_environment():
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    env_path = os.path.join(base_path, ".env")
    if os.path.exists(env_path):
        load_dotenv(env_path)

load_environment()
lang_code = os.getenv("APP_LANG", "en")
t = Translator(lang_code).t

# Configuración de apariencia
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")


class LyricsDisplayApp:
    def __init__(self, root):
        self.root = root
        self.root.title(t("app_title"))
        self.root.geometry("900x900")
        self.root.resizable(True, True)
        self.root.configure(fg_color="#0F0F0F")

        self.fonts = FontManager()
        self.stats = MusicStats()
        self.last_track_id = None
        self.lyrics_data = None
        self.current_line = ""

        self.last_progress_ms = 0
        self.last_update_time = time.time()

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.main_frame = ctk.CTkFrame(self.root, fg_color="#111111", corner_radius=20)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.album_label = ctk.CTkLabel(self.main_frame, text="")
        self.album_label.pack(pady=(30, 10))

        self.title_label = ctk.CTkLabel(self.main_frame, text="", font=self.fonts.get("Bold", 24),
                                        text_color="white", wraplength=760)
        self.title_label.pack()
        self.artist_label = ctk.CTkLabel(self.main_frame, text="", font=self.fonts.get("Medium", 16),
                                         text_color="#A0A0A0", wraplength=760)
        self.artist_label.pack(pady=(0, 20))

        self.lyrics_frame = ctk.CTkFrame(self.main_frame, height=150, corner_radius=15,
                                         fg_color="#1B1B1B")
        self.lyrics_frame.pack(padx=30, pady=15, fill="x")
        self.lyrics_frame.pack_propagate(False)

        self.prev_label = ctk.CTkLabel(self.lyrics_frame, text="", font=self.fonts.get("Light", 16),
                                       text_color="#555", wraplength=680)
        self.prev_label.pack(pady=5)

        self.curr_label = ctk.CTkLabel(self.lyrics_frame, text=t("waiting_for_song"), font=self.fonts.get("SemiBold", 22),
                                       text_color="#1DB954", wraplength=680)
        self.curr_label.pack(pady=5)

        self.next_label = ctk.CTkLabel(self.lyrics_frame, text="", font=self.fonts.get("Light", 16),
                                       text_color="#555", wraplength=680)
        self.next_label.pack(pady=5)

        self.time_label = ctk.CTkLabel(self.main_frame, text="00:00 / 00:00",
                                       font=self.fonts.get("Regular", 14), text_color="#A0A0A0")
        self.time_label.pack(padx=20, pady=(0, 5), anchor="e")

        self.progress = ctk.CTkProgressBar(self.main_frame, height=15, corner_radius=10, progress_color="#1DB954")
        self.progress.set(0)
        self.progress.pack(padx=30, pady=10, fill="x")

        self.controls_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.controls_frame.pack(pady=10)

        buttons = [
            {"emoji": "<", "command": self.prev_track},
            {"emoji": "|", "command": self.toggle_play_pause},
            {"emoji": ">", "command": self.next_track},
            {"emoji": "📊", "command": self.show_stats}
        ]

        for btn in buttons:
            b = ctk.CTkButton(self.controls_frame, text=btn["emoji"], command=btn["command"],
                              width=65, height=50, font=self.fonts.get("SemiBold", 20),
                              corner_radius=12, fg_color="#222", hover_color="#1DB954",
                              text_color="white")
            b.pack(side="left", padx=12)

        self.update_loop()

    def update_loop(self):
        info = get_current_playing_track()
        now = time.time()

        if info:
            if info["id"] != self.last_track_id:
                self.stats.new_track(info)
                self.lyrics_data = self.fetch_lyrics(info)
                self.last_track_id = info["id"]
                self.update_metadata(info)
                self.last_progress_ms = info["progress_ms"]
                self.last_update_time = now
            else:
                elapsed = (now - self.last_update_time) * 1000
                self.last_progress_ms += elapsed
                self.last_update_time = now

            duration_ms = info["duration"]
            current_ms = min(self.last_progress_ms, duration_ms)

            self.progress.set(current_ms / duration_ms)
            self.time_label.configure(text=f"{self.format_ms(current_ms)} / {self.format_ms(duration_ms)}")

            if self.lyrics_data and self.lyrics_data["status"] == "found":
                current_time = current_ms / 1000
                prev, curr, next_ = self.get_lyrics_window(self.lyrics_data["lyrics"], current_time)
                self.prev_label.configure(text=prev)
                self.curr_label.configure(text=curr)
                self.next_label.configure(text=next_)
            else:
                self.curr_label.configure(text=t("no_lyrics_found"), text_color="red")
                self.prev_label.configure(text="")
                self.next_label.configure(text="")
        else:
            if self.last_track_id:
                self.stats.new_track(None)
                self.last_track_id = None
            self.curr_label.configure(text=t("no_song"), text_color="gray")
            self.prev_label.configure(text="")
            self.next_label.configure(text="")
            self.progress.set(0)
            self.time_label.configure(text="00:00 / 00:00")

        self.root.after(500, self.update_loop)

    def fetch_lyrics(self, info):
        res = provider_lrclib(info)
        return res if isinstance(res, dict) and res.get("status") == "found" else {"status": "not_found", "lyrics": []}

    def get_lyrics_window(self, lyrics, current_time):
        for i, line in enumerate(lyrics):
            start = line["time"]
            end = lyrics[i + 1]["time"] if i + 1 < len(lyrics) else float("inf")
            if start <= current_time < end:
                prev = lyrics[i - 1]["line"] if i > 0 else ""
                curr = line["line"]
                next_ = lyrics[i + 1]["line"] if i + 1 < len(lyrics) else ""
                return prev, curr, next_
        return "", "", ""

    def update_metadata(self, info):
        self.title_label.configure(text=info["title"])
        self.artist_label.configure(text=info["artist"])
        try:
            response = requests.get(info["album_image_url"])
            img = Image.open(BytesIO(response.content)).resize((200, 200))
            mask = Image.new("L", img.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.rounded_rectangle((0, 0, 200, 200), radius=30, fill=255)
            img.putalpha(mask)
            album_img = CTkImage(light_image=img, size=(200, 200))
            self.album_label.configure(image=album_img, text="")
            self.album_label.image = album_img
        except Exception as e:
            print(f"[ERROR] {t('error_loading_cover')}: {e}")

    def format_ms(self, ms):
        seconds = int(ms // 1000)
        minutes = seconds // 60
        return f"{minutes:02d}:{seconds % 60:02d}"

    def prev_track(self):
        try:
            sp.previous_track()
        except Exception as e:
            print("[Spotify]", t("spotify_error_prev") + ":", e)

    def next_track(self):
        try:
            sp.next_track()
        except Exception as e:
            print("[Spotify]", t("spotify_error_next") + ":", e)

    def toggle_play_pause(self):
        try:
            playback = sp.current_playback()
            if playback and playback["is_playing"]:
                sp.pause_playback()
            else:
                sp.start_playback()
        except Exception as e:
            print("[Spotify]", t("spotify_error_pause_resume") + ":", e)

    def show_stats(self):
        try:
            StatsWindow(self.root, self.stats)
        except Exception as e:
            print(f"[ERROR] {t('error_showing_stats')}: {e}")


if __name__ == "__main__":
    app = LyricsDisplayApp(ctk.CTk())
    app.root.mainloop()
