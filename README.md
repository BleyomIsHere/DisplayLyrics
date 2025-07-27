# 🎵 Spotify Lyrics & Stats App

A sleek, real-time desktop application that shows synchronized lyrics and detailed listening statistics for your current Spotify playback.

Built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) and inspired by modern UI aesthetics like Spotify, Discord, and Apple Music.

---

## ✨ Features

- 🎶 **Live Lyrics**  
  Shows synchronized lyrics line-by-line, with smooth transitions and a karaoke-style display.

- 📊 **Music Stats Dashboard**  
  Visualize your top tracks, artists, albums, favorite listening hour, daily averages, and more.

- 🖱️ **Playback Controls**  
  Control your current Spotify playback (next, previous, play/pause) right from the app.

- 🌍 **Multi-language Support**  
  Available in English and Spanish (easy to extend).

---

## 🛠️ Requirements

- Python 3.10+
- A Spotify Developer App (for authentication)
- Your own `.env` file with:
  ```
  SPOTIPY_CLIENT_ID=your_client_id
  SPOTIPY_CLIENT_SECRET=your_client_secret
  SPOTIPY_REDIRECT_URI=http://localhost:8888/callback
  APP_LANG=en
  ```

---

## 🧱 Installation

```bash
git clone https://github.com/your-username/spotify-lyrics-stats.git
cd spotify-lyrics-stats
pip install -r requirements.txt
python lyrics_display.py
```

---

## 📂 Project Structure

```
spotify-lyrics-stats/
│
├── lyrics_display.py           # Main application
├── requirements.txt
├── .env                        # Spotify credentials
│
├── /utils/
│   ├── font_manager.py         # Loads and manages Inter font family
│   ├── i18n.py                 # Translator class (i18n system)
│   ├── providers.py            # LRC file provider (e.g., lrcLib)
│   ├── spotify.py              # Handles Spotify API
│   └── stats.py                # MusicStats logic + StatsWindow GUI
│
├── /lang/
│   ├── en.json                 # English translations
│   └── es.json                 # Spanish translations
│
└── /data/
    └── music_stats.json        # Local cache for listening stats
```

---

## 🚀 Roadmap

- [x] Responsive lyrics display
- [x] Stats dashboard with multiple views
- [x] Multi-language support
- [ ] Compact floating mode (minimal UI)
- [ ] More lyric sources (fallback support)
- [ ] Export stats as image or PDF

---

## 📸 Screenshots

![App screenshot](https://i.imgur.com/LRyesOW.png)
![App screenshot](https://i.imgur.com/ez1Cid6.png)

---

## 🤝 Contributing

Pull requests are welcome!  
If you’d like to suggest features or report bugs, feel free to open an issue.

---
