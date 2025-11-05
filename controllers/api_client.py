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
            "videoId": song.get("videoId")
        }
        for song in songs[:limit]
    ]


# Function that search for songs by title
def get_song_titles(song_title, limit=10):
    """

    """
    results = ytmusic.search(song_title, filter="songs")
    if not results:
        return None

    return [
        {
            "title": song["title"],
            "artist": song["artists"][0]["name"],
            "album": song.get("album", {}).get("name", "Unknown"),
            "videoId": song.get("videoId")
        }
        for song in results[:limit] # Returns a list of song metadata.
    ]


# Function that fetch weekly top songs from YouTube Music charts. (Default country = 'US')
def get_weekly_top_10(country="US"):
    charts = ytmusic.get_charts(country=country)
    top_songs = charts.get("songs", [])[:10]
    if not top_songs:
        print("No top songs found.")
        return None

    return [
        {
            "rank": idx + 1,
            "title": song["title"],
            "artist": song["artists"][0]["name"],
            "videoId": song.get("videoId")
        }
        for idx, song in enumerate(top_songs)
    ]


# Get Playlist Info
def get_playlist(playlist_id):
    """
    Get playlist metadata and its tracks using playlistId.
    """
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


# Example Test Run ===

print(get_playlist('OLAK5uy_kKuGqoUQo37hejjtZXF1ALYGh1gSXjcUQ'))

if __name__ == "__main__":
    print("=== YouTube Music Weekly Top 10 ===")
    top_10 = get_weekly_top_10()
    if top_10:
        for song in top_10:
            print(f"{song['rank']}. {song['title']} - {song['artist']} (videoId={song['videoId']})")

    print("\n=== Search Artist Example ===")
    artist_songs = get_artist_songs("Taylor Swift")
    if artist_songs:
        for idx, s in enumerate(artist_songs, start=1):
            print(f"{idx}. {s['title']} - {s['artist']} ({s['album']})")

    print("\n=== Search Song Example ===")
    song_results = get_song_titles("Blinding Lights")
    if song_results:
        for idx, s in enumerate(song_results, start=1):
            print(f"{idx}. {s['title']} - {s['artist']} ({s['album']})")
