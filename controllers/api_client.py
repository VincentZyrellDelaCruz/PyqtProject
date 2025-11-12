from ytmusicapi import YTMusic

# Initialize ytmusicapi
ytmusic = YTMusic()

# Search Artists by name.
def search_artists(artist_name):
    results = ytmusic.search(artist_name, filter="artists")
    if not results:
        return None

    return results # Returns a list of matching artist data (id, name, subscribers, etc.)


# Function that get artist songs.
def get_artist_songs(artist_name, limit=10):
    artists = search_artists(artist_name)
    if not artists:
        print("Artist not found.")
        return None

    artist = artists[0]
    artist_browse_id = artist.get("browseId")
    if not artist_browse_id:
        print("No browseId found for artist.")
        return None

    artist_data = ytmusic.get_artist(artist_browse_id)
    songs = artist_data.get("songs", {}).get("results", [])
    if not songs:
        print("No songs found for this artist.")
        return None

    return [
        {
            "title": song["title"],
            "artist": song["artists"][0]["name"],
            "album": song.get("album", {}).get("name", "Unknown"),
            "videoId": song.get("videoId"),
            "thumbnails": song.get("thumbnails", [{}])[-1].get("url")
        }
        for song in songs[:limit]
    ]


# Function that search for songs by title
def get_song_titles(song_title, limit=10):
    results = ytmusic.search(song_title, filter="songs")
    if not results:
        return None

    return [
        {
            "title": song["title"],
            "artist": song["artists"][0]["name"],
            "album": song.get("album", {}).get("name", "Unknown"),
            "videoId": song.get("videoId"),
            "thumbnails": song.get("thumbnails", [{}])[-1].get("url")
        }
        for song in results[:limit] # Returns a list of song metadata.
    ]


# Function that fetch weekly top songs from YouTube Music charts. (Currently doesn't work)
def get_weekly_top_10(country="US"):
    try:
        charts = ytmusic.get_charts(country=country)

        # Find the "Top 100 Music Videos" playlist (most consistent source of top songs)
        top_playlist = None
        for item in charts.get("videos", []):
            if "Top" in item["title"] and "Music" in item["title"]:
                top_playlist = item
                break

        if not top_playlist:
            print(f"No top music playlist found for {country}.")
            return None

        playlist_id = top_playlist["playlistId"]

        # Fetch actual songs from the playlist
        playlist = ytmusic.get_playlist(playlist_id, limit=10)
        if not playlist or "tracks" not in playlist:
            print("No tracks found in playlist.")
            return None

        top_10 = []
        for idx, track in enumerate(playlist["tracks"][:10]):
            title = track.get("title", "Unknown Title")
            artist_name = (
                track["artists"][0]["name"] if track.get("artists") else "Unknown Artist"
            )
            video_id = track.get("videoId")
            thumbnail = (
                track["thumbnails"][-1]["url"]
                if track.get("thumbnails")
                else None
            )

            top_10.append({
                "rank": idx + 1,
                "title": title,
                "artist": artist_name,
                "video_id": video_id,
                "thumbnail": thumbnail
            })

        return top_10

    except Exception as e:
        print(f"Error fetching charts: {e}")
        return None


# Function that fetches top artists from YouTube Music charts
def get_top_artists(country="US", limit=5):
    try:
        charts = ytmusic.get_charts(country=country)
        top_artists = charts.get("artists")
        if not top_artists:
            print(f"No top artists found for country '{country}'.")
            return None

        return [
            {
                "rank": idx + 1,
                "name": artist.get("title", "Unknown Artist"),  # fallback to 'title' instead of 'name'
                "videoId": artist.get("videoId"),
                "thumbnails": artist.get("thumbnails", [{}])[-1].get("url")
            }
            for idx, artist in enumerate(top_artists[:limit])
        ]

    except Exception as e:
        print(f"Error fetching top artists: {e}")
        return None

# Function that fetches new albums and singles from YouTube Music Explore page
def get_new_albums_and_singles(limit=5):
    """
    Fetch new albums and singles from YouTube Music's Explore page.
    Returns a list of dicts with title, artist, browseId, and thumbnail.
    """
    try:
        explore_data = ytmusic.get_explore()  # returns a dict
        sections = explore_data.get("sections", [])

        # Look for a section with 'New releases' or similar variants
        new_releases_section = next(
            (section for section in sections if section.get("title", "").lower() in ["new releases", "new release"]),
            None
        )

        if not new_releases_section:
            print("No 'New releases' section found in explore data.")
            return []

        items = new_releases_section.get("items", [])
        if not items:
            print("No albums or singles found in 'New releases' section.")
            return []

        albums = []
        for item in items[:limit]:
            # Extract title
            title = item.get("title", "Unknown Title")

            # Artist info can appear in different formats
            subtitle = item.get("subtitle")
            artist = "Unknown Artist"

            if isinstance(subtitle, list) and subtitle:
                # Some entries have [{'name': 'Artist Name', 'browseId': '...'}]
                artist = subtitle[0].get("name", "Unknown Artist")
            elif isinstance(subtitle, str):
                artist = subtitle
            elif "artists" in item:
                artist = ", ".join(a.get("name", "") for a in item["artists"])

            # Thumbnail handling
            thumbnails = item.get("thumbnails", [])
            thumbnail_url = ""
            if thumbnails and isinstance(thumbnails, list):
                thumbnail_url = thumbnails[-1].get("url", "")

            albums.append({
                "title": title,
                "artist": artist,
                "browseId": item.get("browseId"),
                "thumbnails": thumbnail_url
            })

        return albums

    except Exception as e:
        print(f"Error fetching new albums and singles: {e}")
        return []

# Get Playlist Info
def get_playlist(playlist_id):
    # Get playlist metadata and its tracks using playlistId.
    playlist = ytmusic.get_playlist(playlist_id, limit=20)
    if not playlist:
        return None

    tracks = [
        {
            "title": track["title"],
            "artist": track["artists"][0]["name"],
            "videoId": track.get("videoId")
        }
        for track in playlist["tracks"]
    ]

    return {
        "title": playlist.get("title"),
        "description": playlist.get("description"),
        "tracks": tracks
    }

# Function that fetches 5 recommended songs from YouTube Music
def get_recommended_songs(limit=5):
    try:
        home = ytmusic.get_home()
        for section in home:
            contents = section.get("contents", [])
            # Filter for song-type items with videoId and title
            song_items = [
                item for item in contents
                if item.get("videoId") and item.get("title") and "artists" in item
            ]
            if song_items:
                return [
                    {
                        "title": item["title"],
                        "artist": item["artists"][0].get("name", "Unknown Artist"),
                        "album": item.get("album", {}).get("name", "Unknown Album"),
                        "videoId": item["videoId"],
                        "thumbnails": item.get("thumbnails", [{}])[-1].get("url")
                    }
                    for item in song_items[:limit]
                ]

        print("No recommended songs found in home sections.")
        return None

    except Exception as e:
        print(f"Error fetching recommended songs: {e}")
        return None

# Function for fetching all genres
def get_genres():
    try:
        genres = ytmusic.get_mood_categories()
        genres = genres.get("Genres", [])
        if not genres:
            print("No genres found in 'Genres' section.")
            return None

        # print(genres)

        return [
            {
                'title': genre.get("title"),
                'params': genre.get("params")
            }
            for genre in genres
        ]
    except Exception as e:
        print(f"Error fetching genres: {e}")
        return None

# Function for fetching songs based on a genre (Didn't work on most genres)
def get_genre_songs(params=None):
    try:
        genre_songs = ytmusic.get_mood_playlists(params)

        print(genre_songs)
    except Exception as e:
        print(f"Error fetching genre songs: {e}")
        return None


# Example Test Run ===
if __name__ == "__main__":
    # print(get_playlist('OLAK5uy_kKuGqoUQo37hejjtZXF1ALYGh1gSXjcUQ'))
    '''
    print("\n=== Recommended Songs ===")
    recommended = get_recommended_songs()
    if recommended:
        for idx, song in enumerate(recommended, start=1):
            print(f"{idx}. {song['title']} - {song['artist']} ({song['album']}) {song['thumbnails']}")

    print("=== YouTube Music Weekly Top 10 ===")
    top_10 = get_weekly_top_10()
    if top_10:
        for song in top_10:
            print(f"{song['rank']}. {song['title']} - {song['artist']} (videoId={song['video_id']}) ({song['thumbnail']})")

    print("\n=== YouTube Music Top Artists ===")
    top_artists = get_top_artists()
    if top_artists:
        for artist in top_artists:
            print(f"{artist['rank']}. {artist['name']} {artist['thumbnails']}")

    print("\n=== Search Artist Example ===")
    artist_songs = get_artist_songs("Taylor Swift")
    if artist_songs:
        for idx, s in enumerate(artist_songs, start=1):
            print(f"{idx}. {s['title']} - {s['artist']} ({s['album']}) {s['thumbnails']}")

    print("\n=== Search Song Example ===")
    song_results = get_song_titles("Blinding Lights")
    if song_results:
        for idx, s in enumerate(song_results, start=1):
            print(f"{idx}. {s['title']} - {s['artist']} ({s['album']}) {s['thumbnails']}")

    print("US Charts:", ytmusic.get_charts(country="US"))
    '''
    '''
    genres = get_genres()
    for genre in genres:
        print(f"{genre['title']} {genre['params']}")

    get_genre_songs('ggMPOg1uXzdlSXhKZ0hMV1Z4')
    '''
