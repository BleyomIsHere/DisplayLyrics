# 🎵 Spotify Lyrics Display

A desktop app to display **real-time synced lyrics** from any active Spotify session linked to your account.  
It doesn’t matter if the song is playing on your phone, tablet, web, or desktop — the lyrics sync with *your* account's current playback.

---

## 🖼️ Screenshots

![App screenshot](https://i.imgur.com/LRyesOW.png)  
![App screenshot](https://i.imgur.com/ez1Cid6.png)

---

## ✅ Features

- 🔄 Real-time synchronized lyrics (previous / current / next)
- 🖼️ Album art, track title and artist name
- 🎛 Spotify controls: play/pause, skip, rewind
- 📊 Listening stats (optional)
- 🌐 Multi-language support (EN 🇺🇸 / ES 🇪🇸)

> 💡 This works even if the song is playing from your phone, browser, or another device — as long as it’s using your Spotify account.

---

## 🚀 Download

👉 [**Latest Release (Windows EXE)**](https://github.com/BleyomIsHere/DisplayLyrics/releases/latest)

Download the latest `.exe` from the **Releases** section and run it — no installation required.

> ⚠️ Make sure your `.env` file is correctly configured in the same folder as the `.exe`.


## 🧰 Step-by-Step Setup

### 1. **Install Python**

Install Python 3.10 or higher:  
👉 https://www.python.org/downloads/

---

### 2. **Create a Spotify App**

Go to: [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)

1. Click **Create an App**
2. Add a name and description (e.g. *Lyrics App*)
3. Set the Redirect URI to:

    ```
    http://localhost:8888/callback
    ```

4. Save changes
5. Copy your **Client ID** and **Client Secret**

---

### 3. **Set up `.env`**

In the project root (where `main.py` is), create a file called `.env` with this content:

```env
SPOTIPY_CLIENT_ID=your_spotify_client_id
SPOTIPY_CLIENT_SECRET=your_spotify_client_secret
SPOTIPY_REDIRECT_URI=http://localhost:8888/callback
APP_LANG=en
```

Set `APP_LANG=es` for Spanish.

---

### 4. **Install Dependencies**

```bash
pip install -r requirements.txt
```

---

### 5. **Run the App**

```bash
python main.py
```

✅ That’s it — lyrics should appear if something is playing on any of your Spotify sessions.

---

## 📁 Project Structure

```
├── main.py                  # Main app entry point
├── utils/                  # Helper modules (Spotify, lyrics, etc.)
├── assets/                 # Fonts and images
├── lang/                   # Translations (en.json, es.json)
├── .env                    # Local config (ignored)
├── README.md
├── requirements.txt
```

---

## 🪟 Platform Support

- ✅ Windows 10/11 — Full support
- ⚠️ WSL (Linux Subsystem) — Works, but playback controls may not respond
- 🧪 Linux/Mac — Not officially tested

---

## 🔨 Building a Windows EXE (Optional)

If you want to create an `.exe`:

```bash
pyinstaller main.py --noconfirm --onefile ^
--add-data "utils;utils" ^
--add-data "lang;lang" ^
--add-data "assets;assets" ^
--name main
```

Make sure `.env` is manually added to the build directory after compiling.

---

## 🧊 Status

This is a hobby project — not a commercial app.  
It works fine and is fun to use, but it's not pretending to be perfect.

---

## 🛠 Credits

- Lyrics from [lrclib.net](https://lrclib.net/)
- Spotify integration via [Spotipy](https://spotipy.readthedocs.io/)
- UI built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)

---

## 🙌 Want to contribute?

If you’d like to improve it or suggest something, feel free to open an issue or PR.  
Let’s keep it simple and useful.

---

## 📄 License

MIT License

