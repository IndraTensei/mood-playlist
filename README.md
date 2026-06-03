# mood-playlist 🎵

> *Tell it how you're feeling. It'll find the perfect tunes.*

**mood-playlist** is a fun, colorful CLI tool that generates curated Spotify playlists based on your current mood. Whether you're coding, heartbroken, hype for the weekend, or just vibing on a rainy afternoon — there's a playlist for that.

![Python](https://img.shields.io/badge/Python-3.7%2B-blue?style=flat-square&logo=python)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Spotify](https://img.shields.io/badge/Spotify-API-1DB954?style=flat-square&logo=spotify)

## ✨ Features

- **15 mood profiles** — from `happy` to `zen`, `angry` to `roadtrip`, and even `coding` mode 💻
- **Spotify Recommendations API integration** — real tracks, real artists, real vibes
- **Interactive mode** — guided mood picker if you can't decide what you're feeling
- **Demo mode** — see how it works without any API keys
- **Export options** — save playlists as M3U or JSON files
- **Beautiful CLI output** — colored tables, emojis, and formatted track listings
- **No bloat** — single Python file, zero config, gets straight to the music

## 🚀 Installation

### From source (recommended)

```bash
# Clone the repo
git clone https://github.com/IndraTensei/mood-playlist.git
cd mood-playlist

# Install dependency
pip install requests

# Make it executable (Linux / macOS)
chmod +x mood-playlist.py

# Optional: add to PATH
sudo ln -s "$(pwd)/mood-playlist.py" /usr/local/bin/mood-playlist
```

### Requirements
- Python 3.7+
- `requests` library (`pip install requests`)
- A [Spotify Developer](https://developer.spotify.com/dashboard) account (free)

## 🔑 Spotify Setup (one-time, 2 minutes)

1. Go to [https://developer.spotify.com/dashboard](https://developer.spotify.com/dashboard)
2. Create an app (any name works; set Redirect URI to `http://localhost:8888/callback`)
3. Copy your **Client ID** and **Client Secret**
4. Set them as environment variables or pass them directly:

```bash
# Option A: Environment variables (persistent)
export SPOTIFY_CLIENT_ID="your-client-id-here"
export SPOTIFY_CLIENT_SECRET="your-client-secret-here"

# Option B: Pass them inline
mood-playlist happy --client-id YOUR_ID --client-secret YOUR_SECRET
```

## 🎮 Usage

### Quick Start

```bash
# Generate a happy playlist
mood-playlist happy

# Generate a chill playlist with 10 tracks
mood-playlist chill --limit 10

# Demo mode (no API keys needed!)
mood-playlist energetic --demo
```

### All Options

| Flag | Description | Default |
|------|-------------|---------|
| `<mood>` | Your mood (see list below) | — |
| `--list`, `-l` | Show all available moods | — |
| `--interactive`, `-i` | Interactive mood picker | — |
| `--limit N`, `-n N` | Number of tracks | 20 |
| `--demo` | Demo mode (no API needed) | — |
| `--export-m3u` | Export as M3U playlist file | — |
| `--export-json` | Export as JSON file | — |
| `--no-links` | Hide Spotify links in output | — |
| `--output DIR`, `-o DIR` | Export directory | `.` |
| `--client-id ID` | Spotify Client ID | env var |
| `--client-secret SECRET` | Spotify Client Secret | env var |
| `--version`, `-v` | Show version | — |

### Export Playlists

```bash
# Save as M3U (compatible with most music players)
mood-playlist party --export-m3u --output ~/Music/

# Save as JSON (for apps and scripts)
mood-playlist focused --export-json --output ~/playlists/

# Both at once!
mood-playlist roadtrip --export-m3u --export-json --output ./exports/
```

### Interactive Mode

```bash
mood-playlist --interactive
```

This launches a guided prompt where you pick your mood and get an instant playlist. Great for when you're not sure what you're feeling!

## 🎭 Available Moods

| Mood | Description | Energy | Vibe |
|------|-------------|--------|------|
| `happy` | 😄 Feel-good upbeat pop | HIGH | Positive |
| `sad` | 😢 Melancholic acoustic | LOW | Reflective |
| `chill` | 🌊 Lo-fi relaxation | LOW | Calm |
| `focused` | 🎯 Deep work instrumentals | MID | Neutral |
| `energetic` | ⚡ Workout bangers | HIGH | Hype |
| `romantic` | 💕 Smooth love songs | MID | Warm |
| `angry` | 🔥 Heavy metal & punk | HIGH | Intense |
| `nostalgic` | 🕰️ Classic hits & retro | MID | Nostalgic |
| `party` | 🎉 Dance floor anthems | HIGH | Euphoric |
| `sleepy` | 🌙 Wind-down ambient | LOW | Peaceful |
| `rainy` | 🌧️ Cozy rainy day folk | MID | Melancholy |
| `roadtrip` | 🚗 Adventure & country rock | HIGH | Free |
| `coding` | 💻 Electronic & chiptune | MID | Focused |
| `hype` | 🔊 Bass-heavy hip-hop | HIGH | Aggressive |
| `zen` | 🧘 Meditation & ambient | LOW | Peaceful |

## 💡 Pro Tips

- **Combine with Spotify URI**: Copy the track URLs from the output and open them directly in the Spotify app
- **Shell aliases**: Add to your `.bashrc` or `.zshrc` for quick access:
  ```bash
  alias vibes="mood-playlist --interactive"
  alias jams="mood-playlist energetic --export-json -o ~/playlists/"
  ```
- **Script it**: Pipe the JSON export into your own tools:
  ```bash
  mood-playlist coding --export-json | jq '.tracks[] | .spotify_url'
  ```

## 🤝 Contributing

Contributions are welcome! Here's how:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add: amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Ideas for contributions:**
- Add more mood profiles (yoga? cooking? heartbreak recovery arc?)
- Integrate other music APIs (Apple Music, YouTube Music, Last.fm)
- Add a `TUI` mode with `curses` or `rich` for a full-screen experience
- Support for creating actual Spotify playlists via OAuth (write access)
- Playlist history / favorites

## 📜 License

[MIT](https://opensource.org/licenses/MIT) — use it, remix it, share it. Just have fun. 🎶

---

Made with 🎵 and `requests` by indie developers who believe every mood deserves a soundtrack.
