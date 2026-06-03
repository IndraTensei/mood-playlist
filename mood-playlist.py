#!/usr/bin/env python3
"""
mood-playlist 🎵
Generate curated Spotify playlists based on your mood.

A fun universal CLI tool — tell it how you're feeling, get songs!
"""

import argparse
import json
import os
import sys
import textwrap
from pathlib import Path

try:
    import requests
except ImportError:
    print("❌ Error: 'requests' package required. Install with: pip install requests")
    sys.exit(1)

# ─── Mood-to-genre/tag mapping ────────────────────────────────────────────────

MOOD_PROFILES = {
    # mood: (display_name, genres, energy, valence, description, emoji)
    "happy": (
        "Happy / Feel-Good",
        ["happy", "pop", "feel-good", "sunshine", "dance"],
        0.7, 0.9,
        "Upbeat tracks to keep that smile going 😄",
        "😄",
    ),
    "sad": (
        "Sad / Melancholy",
        ["sad", "acoustic", "indie", "ambient", "piano"],
        0.3, 0.2,
        "Songs for when you need to feel your feelings 💧",
        "😢",
    ),
    "chill": (
        "Chill / Relaxed",
        ["chill", "lo-fi", "ambient", "acoustic", "sleep"],
        0.3, 0.6,
        "Mellow vibes for unwinding 🌊",
        "🌊",
    ),
    "focused": (
        "Focus / Deep Work",
        ["study", "classical", "piano", "ambient", "instrumental"],
        0.4, 0.5,
        "Concentration-boosting instrumentals 🧠",
        "🎯",
    ),
    "energetic": (
        "Energetic / Hype",
        ["workout", "edm", "rock", "hard-rock", "drum-and-bass"],
        0.9, 0.8,
        "High-octane tracks to power through ⚡",
        "⚡",
    ),
    "romantic": (
        "Romantic / Love Songs",
        ["romance", "r-n-b", "soul", "jazz", "love-songs"],
        0.5, 0.7,
        "Smooth grooves for date night 🕯️",
        "💕",
    ),
    "angry": (
        "Angry / Rage",
        ["metal", "hard-rock", "punk", "grindcore", "industrial"],
        0.95, 0.3,
        "Let it out with heavy riffs 🔥",
        "🔥",
    ),
    "nostalgic": (
        "Nostalgic / Throwback",
        ["oldies", "80s", "90s", "classic-rock", "retro"],
        0.6, 0.6,
        "Transport yourself back in time 🕰️",
        "🕰️",
    ),
    "party": (
        "Party / Dance",
        ["party", "dance", "pop", "disco", "electronic"],
        0.85, 0.85,
        "Turn any room into a dance floor 🎉",
        "🎉",
    ),
    "sleepy": (
        "Sleepy / Wind Down",
        ["sleep", "ambient", "new-age", "meditation", "chill"],
        0.15, 0.4,
        "Drift off peacefully 🌙",
        "🌙",
    ),
    "rainy": (
        "Rainy Day",
        ["rainy-day", "acoustic", "folk", "indie", "singer-songwriter"],
        0.4, 0.45,
        "Perfect soundtrack for a cozy rainy afternoon 🌧️",
        "🌧️",
    ),
    "roadtrip": (
        "Road Trip / Adventure",
        ["road-trip", "country", "rock", "indie", "folk"],
        0.7, 0.75,
        "Windows down, music up 🚗",
        "🚗",
    ),
    "coding": (
        "Coding / Developer",
        ["electronic", "chiptune", "ambient", "idm", "post-rock"],
        0.5, 0.55,
        "Beats to ship features to 💻",
        "💻",
    ),
    "hype": (
        "Hype / Pump Up",
        ["hip-hop", "trap", "workout", "drill", "bass-line"],
        0.85, 0.75,
        "Get amped up with bass-heavy bangers 🔊",
        "🔊",
    ),
    "zen": (
        "Zen / Meditation",
        ["meditation", "ambient", "new-age", "classical", "world-music"],
        0.2, 0.5,
        "Inner peace through sound 🧘",
        "🧘",
    ),
}

# ASCII art banner
BANNER = r"""
  __  __                 _  ____  _             _ _       
 |  \/  | ___   ___   __| ||  _ \| | __ _ _   _| (_) ___  
 | |\/| |/ _ \ / _ \ / _` || |_) | |/ _` | | | | | |/ _ \ 
 | |  | | (_) | (_) | (_| ||  __/| | (_| | |_| | | | (_) |
 |_|  |_|\___/ \___/ \__,_||_|   |_|\__,_|\__, |_|_|\___/ 
                                           |___/           
🎵  Mood-based playlist generator  🎵
"""


def colorize(text: str, color: str) -> str:
    """Add ANSI color codes."""
    colors = {
        "red": "\033[91m", "green": "\033[92m", "yellow": "\033[93m",
        "blue": "\033[94m", "magenta": "\033[95m", "cyan": "\033[96m",
        "white": "\033[97m", "bold": "\033[1m", "reset": "\033[0m",
    }
    c = colors.get(color, "")
    r = colors["reset"]
    return f"{c}{text}{r}" if sys.stdout.isatty() else text


def print_banner():
    if sys.stdout.isatty():
        print(colorize(BANNER, "cyan"))


def list_moods():
    """Print all available moods in a nice table."""
    print(colorize("\n🎭  Available Moods:\n", "bold"))
    for key, (name, _, _, _, desc, emoji) in MOOD_PROFILES.items():
        print(f"  {emoji}  {colorize(key.ljust(12), 'yellow')} — {colorize(name, 'green')}  {colorize(f'({desc})', 'white')}")
    print()


def get_spotify_token(client_id: str, client_secret: str) -> str:
    """Authenticate with Spotify using Client Credentials flow."""
    try:
        resp = requests.post(
            "https://accounts.spotify.com/api/token",
            data={"grant_type": "client_credentials"},
            auth=(client_id, client_secret),
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()["access_token"]
    except requests.exceptions.RequestException as e:
        print(colorize(f"\n❌ Spotify authentication failed: {e}", "red"))
        print("  Make sure your Client ID and Secret are correct.")
        sys.exit(1)


def search_tracks(genres: list, energy: float, valence: float, token: str, limit: int = 20) -> list:
    """Search Spotify for tracks matching the mood profile."""
    all_tracks = []
    headers = {"Authorization": f"Bearer {token}"}

    for genre in genres:
        if len(all_tracks) >= limit:
            break
        try:
            resp = requests.get(
                "https://api.spotify.com/v1/recommendations",
                headers=headers,
                params={
                    "seed_genres": genre,
                    "target_energy": energy,
                    "target_valence": valence,
                    "target_danceability": energy * 0.9,
                    "limit": min(limit, limit - len(all_tracks)),
                    "market": "US",
                },
                timeout=15,
            )
            if resp.status_code == 200:
                tracks = resp.json().get("tracks", [])
                all_tracks.extend(tracks)
        except requests.exceptions.RequestException:
            continue

    return all_tracks[:limit]


def display_playlist(tracks: list, mood: str, mood_name: str, emoji: str):
    """Display the playlist in a nice formatted table."""
    if not tracks:
        print(colorize("\n😔  No tracks found. Try a different mood or check your connection.", "yellow"))
        return

    print(colorize(f"\n{emoji}  Your {mood_name} Playlist:", "bold"))
    print(colorize(f"   {len(tracks)} tracks based on mood '{mood}'\n", "cyan"))
    print(colorize(f"  {'#':<4} {'Track':<45} {'Artist':<30} {'Album':<30}", "bold"))
    print(colorize("  " + "─" * 109, "white"))

    for i, track in enumerate(tracks, 1):
        name = track.get("name", "Unknown")[:44]
        artist = ", ".join(a["name"] for a in track.get("artists", []))[:29]
        album = track.get("album", {}).get("name", "N/A")[:29]
        duration = track.get("duration_ms", 0)
        mins, secs = divmod(duration // 1000, 60)
        print(f"  {i:<4} {name:<45} {artist:<30} {album:<25} {mins}:{secs:02d}")

    print()


def export_m3u(tracks: list, mood: str, output_dir: str = "."):
    """Export playlist as M3U file."""
    filepath = os.path.join(output_dir, f"mood-{mood}.m3u")
    with open(filepath, "w") as f:
        f.write("#EXTM3U\n")
        f.write(f"#PLAYLIST:mood-{mood}\n")
        for track in tracks:
            name = track.get("name", "Unknown")
            artist = ", ".join(a["name"] for a in track.get("artists", []))
            duration = track.get("duration_ms", 0) // 1000
            preview = track.get("preview_url", "")
            f.write(f"#EXTINF:{duration},{artist} - {name}\n")
            f.write(f"# {preview}\n" if preview else f"# No preview available\n")
    print(colorize(f"  📁  Exported M3U playlist to: {filepath}", "green"))


def export_json(tracks: list, mood: str, output_dir: str = "."):
    """Export track list as JSON."""
    filepath = os.path.join(output_dir, f"mood-{mood}.json")
    data = {
        "mood": mood,
        "track_count": len(tracks),
        "tracks": [
            {
                "name": t.get("name", "Unknown"),
                "artist": ", ".join(a["name"] for a in t.get("artists", [])),
                "album": t.get("album", {}).get("name", "N/A"),
                "duration_ms": t.get("duration_ms", 0),
                "spotify_url": t.get("external_urls", {}).get("spotify", ""),
                "preview_url": t.get("preview_url", ""),
            }
            for t in tracks
        ],
    }
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
    print(colorize(f"  📁  Exported JSON playlist to: {filepath}", "green"))


def save_to_spotify(tracks: list, mood: str, token: str):
    """Get shareable Spotify links for the tracks."""
    playlist_name = f"Mood: {mood.capitalize()}"
    print(colorize(f"\n  🎵  \"{playlist_name}\" — {len(tracks)} tracks\n", "bold"))
    print("  Add these to your Spotify library:\n")
    for i, track in enumerate(tracks, 1):
        url = track.get("external_urls", {}).get("spotify", "")
        name = track.get("name", "Unknown")
        artist = ", ".join(a["name"] for a in track.get("artists", []))
        print(f"  {i}. 🎵 {artist} - {name}")
        if url:
            print(f"     🔗 {url}")
    print()


def interactive_mode(args):
    """Run in interactive mode — user selects mood via prompts."""
    print_banner()
    list_moods()

    while True:
        try:
            mood_input = input(colorize("  🎭  How are you feeling? (or 'quit' to exit): ", "cyan")).strip().lower()
        except (EOFError, KeyboardInterrupt):
            print(colorize("\n\n  👋  Goodbye! Stay vibing! 🎶", "cyan"))
            break

        if mood_input in ("quit", "exit", "q"):
            print(colorize("\n  👋  Goodbye! Stay vibing! 🎶", "cyan"))
            break

        if mood_input not in MOOD_PROFILES:
            print(colorize(f"  ⚠️  Unknown mood '{mood_input}'. Run with --list to see available moods.\n", "yellow"))
            continue

        args.mood = mood_input
        args.interactive = False  # prevent infinite loop
        run_playlist_generation(args)
        print()


def run_playlist_generation(args):
    """Core playlist generation logic."""
    mood = args.mood.lower()
    if mood not in MOOD_PROFILES:
        print(colorize(f"  ⚠️  Unknown mood '{mood}'. Here are available moods:", "yellow"))
        list_moods()
        sys.exit(1)

    profile = MOOD_PROFILES[mood]
    mood_name = profile[0]
    genres = profile[1]
    energy = profile[2]
    valence = profile[3]
    desc = profile[4]
    emoji = profile[5]

    print(colorize(f"\n  {emoji}  Generating your {mood_name} playlist...", "bold"))
    print(colorize(f"     {desc}", "white"))

    # Get Spotify credentials
    client_id = args.client_id or os.environ.get("SPOTIFY_CLIENT_ID", "")
    client_secret = args.client_secret or os.environ.get("SPOTIFY_CLIENT_SECRET", "")

    if not client_id or not client_secret:
        print(colorize("\n  ⚠️  No Spotify credentials provided.", "yellow"))
        print("  You can still use the tool in demo mode with --demo flag,")
        print(f"  or set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET.")
        print("\n  📝  To get credentials:")
        print("     1. Go to https://developer.spotify.com/dashboard")
        print("     2. Create an app (set redirect URI to http://localhost:8888/callback)")
        print("     3. Copy the Client ID and Client Secret\n")
        sys.exit(1)

    # Fetch tracks
    print(f"  🔍  Searching Spotify for {', '.join(genres[:3])}...")
    token = get_spotify_token(client_id, client_secret)
    tracks = search_tracks(genres, energy, valence, token, limit=args.limit or 20)

    if not tracks:
        print(colorize("\n  😔  Could not find tracks. Your credentials may be invalid or rate-limited.", "yellow"))
        sys.exit(1)

    # Display
    display_playlist(tracks, mood, mood_name, emoji)

    # Export options
    if args.export_m3u:
        export_m3u(tracks, mood, args.output or ".")
    if args.export_json:
        export_json(tracks, mood, args.output or ".")
    if not args.no_links:
        save_to_spotify(tracks, mood, token)

    return tracks


def demo_mode(args):
    """Run in demo mode without Spotify API — show what the tool would do."""
    mood = args.mood.lower()
    if mood not in MOOD_PROFILES:
        print(colorize(f"  ⚠️  Unknown mood '{mood}'. Here are available moods:", "yellow"))
        list_moods()
        sys.exit(1)

    profile = MOOD_PROFILES[mood]
    mood_name, genres, energy, valence, desc, emoji = profile

    print(colorize(f"\n  {emoji}  DEMO MODE — {mood_name} Playlist", "bold"))
    print(colorize(f"     {desc}\n", "white"))
    print(f"  📊  Search parameters:")
    print(f"     • Genres:       {', '.join(genres)}")
    print(f"     • Energy:       {energy:.2f}  ({'low' if energy < 0.4 else 'medium' if energy < 0.7 else 'high'})")
    print(f"     • Valence:      {valence:.2f}  ({'negative' if valence < 0.4 else 'neutral' if valence < 0.7 else 'positive'})")
    print(f"     • Danceability: {energy * 0.9:.2f}")
    print(f"     • Limit:        {args.limit or 20} tracks\n")

    print(colorize("  🎵  With a real Spotify account, you'd get tracks like:\n", "bold"))

    # Example track names based on mood
    example_tracks = {
        "happy": [
            ("Walking on Sunshine", "Katrina & the Waves"),
            ("Good as Hell", "Lizzo"),
            ("Happy", "Pharrell Williams"),
            ("Uptown Funk", "Bruno Mars"),
            ("Shake It Off", "Taylor Swift"),
            ("Can't Stop the Feeling", "Justin Timberlake"),
            ("I Gotta Feeling", "Black Eyed Peas"),
            ("Good Vibrations", "The Beach Boys"),
            ("Don't Stop Me Now", "Queen"),
            ("On Top of the World", "Imagine Dragons"),
        ],
        "sad": [
            ("Someone Like You", "Adele"),
            ("Fix You", "Coldplay"),
            ("All I Want", "Kodaline"),
            ("Say Something", "A Great Big World"),
            ("Skinny Love", "Bon Iver"),
            ("The Night We Met", "Lord Huron"),
            ("Let Her Go", "Passenger"),
            ("Breathe Me", "Sia"),
            ("Hurt", "Johnny Cash"),
            ("How to Save a Life", "The Fray"),
        ],
        "chill": [
            ("Weightless", "Marconi Union"),
            ("River", "Leon Bridges"),
            ("Landslide", "Fleetwood Mac"),
            ("Holocene", "Bon Iver"),
            ("Nikes", "Frank Ocean"),
            ("Gooey", "Glass Animals"),
            ("Snow", "Rhye"),
            ("From The Dining Table", "Harry Styles"),
            ("Serotonin", "girl in red"),
            ("Sunset Lover", "Petit Biscuit"),
        ],
        "focused": [
            ("Experience", "Ludovico Einaudi"),
            ("Nuvole Bianche", "Ludovico Einaudi"),
            ("Gymnopédie No. 1", "Erik Satie"),
            ("Spiegel im Spiegel", "Arvo Pärt"),
            ("River Flows in You", "Yiruma"),
            ("Avril 14th", "Aphex Twin"),
            ("Una Mattina", "Ludovico Einaudi"),
            ("Comptine d'un autre été", "Yann Tiersen"),
            ("Time", "Hans Zimmer"),
            ("Interstellar Main Theme", "Hans Zimmer"),
        ],
        "energetic": [
            ("Thunderstruck", "AC/DC"),
            ("Eye of the Tiger", "Survivor"),
            ("Stronger", "Kanye West"),
            ("Till I Collapse", "Eminem"),
            ("Can't Hold Us", "Macklemore"),
            ("XO Tour Llif3", "Lil Uzi Vert"),
            ("Sicko Mode", "Travis Scott"),
            ("Power", "Kanye West"),
            ("DNA.", "Kendrick Lamar"),
            ("Warriors", "Imagine Dragons"),
        ],
        "romantic": [
            ("Thinking Out Loud", "Ed Sheeran"),
            ("All of Me", "John Legend"),
            ("Perfect", "Ed Sheeran"),
            ("At Last", "Etta James"),
            ("Let's Stay Together", "Al Green"),
            ("A Thousand Years", "Christina Perri"),
            ("Just the Way You Are", "Bruno Mars"),
            ("My Funny Valentine", "Chet Baker"),
            ("The Way You Look Tonight", "Frank Sinatra"),
            ("Make You Feel My Love", "Adele"),
        ],
        "angry": [
            ("Break Stuff", "Limp Bizkit"),
            ("Chop Suey!", "System of a Down"),
            ("Killing in the Name", "Rage Against the Machine"),
            ("Bodies", "Drowning Pool"),
            ("Last Resort", "Papa Roach"),
            ("Freak on a Leash", "Korn"),
            ("Wait and Bleed", "Slipknot"),
            ("Ace of Spades", "Motörhead"),
            ("Paranoid", "Black Sabbath"),
            ("Master of Puppets", "Metallica"),
        ],
        "nostalgic": [
            ("Bohemian Rhapsody", "Queen"),
            ("Hotel California", "Eagles"),
            ("Sweet Child O' Mine", "Guns N' Roses"),
            ("Stairway to Heaven", "Led Zeppelin"),
            ("Imagine", "John Lennon"),
            ("No Woman No Cry", "Bob Marley"),
            ("What's Going On", "Marvin Gaye"),
            ("Wonderwall", "Oasis"),
            ("Under the Bridge", "Red Hot Chili Peppers"),
            ("Smells Like Teen Spirit", "Nirvana"),
        ],
        "party": [
            ("Blinding Lights", "The Weeknd"),
            ("Levitating", "Dua Lipa"),
            ("Don't Start Now", "Dua Lipa"),
            ("Dynamite", "BTS"),
            ("WAP", "Cardi B"),
            ("Savage", "Megan Thee Stallion"),
            ("Watermelon Sugar", "Harry Styles"),
            ("Savage Love", "Jawsh 685"),
            ("Rockstar", "DaBaby"),
            ("Good 4 U", "Olivia Rodrigo"),
        ],
        "sleepy": [
            ("Clair de Lune", "Debussy"),
            ("Moonlight Sonata", "Beethoven"),
            ("Gymnopédie No. 3", "Erik Satie"),
            ("Avril 14th", "Aphex Twin"),
            ("Weightless", "Marconi Union"),
            ("Delta Dreams", "Sleep Music"),
            ("Dream a Little Dream", "Mama Cass"),
            ("Strawberry Fields Forever", "The Beatles"),
            ("The Sound of Silence", "Simon & Garfunkel"),
            ("Pale Blue Eyes", "The Velvet Underground"),
        ],
        "rainy": [
            ("Rain", "The Beatles"),
            ("November Rain", "Guns N' Roses"),
            ("Set Fire to the Rain", "Adele"),
            ("Purple Rain", "Prince"),
            ("Have You Ever Seen The Rain", "CCR"),
            ("Here Comes the Sun", "The Beatles"),
            ("Ain't No Sunshine", "Bill Withers"),
            ("Both Sides Now", "Joni Mitchell"),
            ("Singing in the Rain", "Gene Kelly"),
            ("Mad World", "Gary Jules"),
        ],
        "roadtrip": [
            ("Born to Run", "Bruce Springsteen"),
            ("Take Me Home, Country Roads", "John Denver"),
            ("Life is a Highway", "Tom Cochrane"),
            ("On the Road Again", "Willie Nelson"),
            ("Radar Love", "Golden Earring"),
            ("Fast Car", "Tracy Chapman"),
            ("Truckin'", "Grateful Dead"),
            ("Ramblin' Man", "Allman Brothers"),
            ("Route 66", "Chuck Berry"),
            ("Little Deuce Coupe", "The Beach Boys"),
        ],
        "coding": [
            ("Get Lucky", "Daft Punk"),
            ("Digital Love", "Daft Punk"),
            ("Harder, Better, Faster, Stronger", "Daft Punk"),
            ("Around the World", "Daft Punk"),
            ("Midnight City", "M83"),
            ("Instant Crush", "Daft Punk"),
            ("Something About Us", "Daft Punk"),
            ("Veridis Quo", "Daft Punk"),
            ("Touch", "Daft Punk"),
            ("Beyond", "Daft Punk"),
        ],
        "hype": [
            ("HUMBLE.", "Kendrick Lamar"),
            ("Mo Bamba", "Sheck Wes"),
            ("Sicko Mode", "Travis Scott"),
            ("God's Plan", "Drake"),
            ("XO Tour Llif3", "Lil Uzi Vert"),
            ("Bad and Boujee", "Migos"),
            ("Gucci Gang", "Lil Pump"),
            ("Look at Me!", "XXXTENTACION"),
            ("Migos", "Migos"),
            ("No Lie", "21 Savage"),
        ],
        "zen": [
            ("Zen Garden", "Meditation Music"),
            ("Tibetan Bowls", "Sound Bath"),
            ("Inner Peace", "Nature Sounds"),
            ("Om Meditation", "Chanting"),
            ("Singing Bowls", "Healing Frequencies"),
            ("Forest Ambience", "Nature"),
            ("Ocean Waves", "Relaxation"),
            ("Wind Chimes", "Peaceful Sounds"),
            ("Raindrops", "Nature Ambient"),
            ("Sacred Ground", "Native Flute"),
        ],
    }

    tracks_for_mood = example_tracks.get(mood, [])
    for i, (name, artist) in enumerate(tracks_for_mood, 1):
        print(f"  {i}. 🎵 {artist} - {name}")

    print(colorize(f"\n  💡  Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET for real tracks!", "cyan"))
    print()


def main():
    parser = argparse.ArgumentParser(
        prog="mood-playlist",
        description="🎵 Generate music playlists based on your mood",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            examples:
              mood-playlist happy                         # Generate happy playlist
              mood-playlist sad --limit 10                 # 10 sad tracks
              mood-playlist focused --export-json          # Export as JSON file
              mood-playlist happy --export-m3u --output ./playlists
              mood-playlist --list                         # Show all moods
              mood-playlist --interactive                  # Interactive mode
              mood-playlist happy --demo                   # Demo mode (no API needed)
        """),
    )
    parser.add_argument("mood", nargs="?", help="Your current mood (e.g., happy, sad, chill)")
    parser.add_argument("--list", "-l", action="store_true", help="List all available moods")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mood picker")
    parser.add_argument("--limit", "-n", type=int, default=20, help="Number of tracks (default: 20)")
    parser.add_argument("--client-id", help="Spotify Client ID (or set SPOTIFY_CLIENT_ID)")
    parser.add_argument("--client-secret", help="Spotify Client Secret (or set SPOTIFY_CLIENT_SECRET)")
    parser.add_argument("--export-m3u", action="store_true", help="Export playlist as M3U file")
    parser.add_argument("--export-json", action="store_true", help="Export playlist as JSON file")
    parser.add_argument("--no-links", action="store_true", help="Don't show Spotify links")
    parser.add_argument(
        "--output", "-o", default=".", help="Output directory for exports (default: current dir)"
    )
    parser.add_argument("--demo", action="store_true", help="Demo mode — no Spotify API needed")
    parser.add_argument("--version", "-v", action="version", version="mood-playlist 1.0.0")

    args = parser.parse_args()

    # List moods mode
    if args.list:
        print_banner()
        list_moods()
        return

    # Interactive mode
    if args.interactive:
        interactive_mode(args)
        return

    # No mood provided — show help
    if not args.mood:
        print_banner()
        list_moods()
        print(colorize("  👉  Run: mood-playlist <mood> to generate a playlist", "cyan"))
        print(colorize("  👉  Run: mood-playlist --interactive for interactive mode", "cyan"))
        print(colorize("  👉  Run: mood-playlist --help for all options\n", "cyan"))
        return

    # Demo mode
    if args.demo:
        print_banner()
        demo_mode(args)
        return

    # Normal mode
    print_banner()
    run_playlist_generation(args)


if __name__ == "__main__":
    main()
