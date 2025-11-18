from ytmusicapi import YTMusic
import yt_dlp as ytdl

# Initialize ytmusicapi
ytmusic = YTMusic()

# Search Artists by name.
def search_artists(artist_name):
    results = ytmusic.search(artist_name, filter="artists")
    if not results:
        return None

    return results # Returns a list of matching artist data (id, name, subscribers, etc.)


# Function that fetches artist info, albums, and top songs.
def get_artist_metadata(artist_name, limit=10):
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

    top_songs_section = (
        artist_data.get("songs", {}).get("results")
        or artist_data.get("topSongs", {}).get("results")
    )

    if not top_songs_section:
        playlist_id = artist_data.get("songs", {}).get("playlistId")
        if playlist_id:
            playlist = ytmusic.get_playlist(playlist_id, limit=limit)
            top_songs_section = playlist.get("tracks", [])
        else:
            print("No top songs available for this artist.")
            return None

    description = artist_data.get("description", "No description available.")
    artist_image = artist_data.get("thumbnails", [{}])[-1].get("url", "No image available.")

    albums = []
    if "albums" in artist_data:
        for alb in artist_data["albums"].get("results", []):
            albums.append({
                "title": alb.get("title"),
                "year": alb.get("year"),
                "browseId": alb.get("browseId"),
                "thumbnails": alb.get("thumbnails", [{}])[-1].get("url") if alb.get("thumbnails") else None,
                "type": "Album"
            })
    if "singles" in artist_data:
        for sng in artist_data["singles"].get("results", []):
            albums.append({
                "title": sng.get("title"),
                "year": sng.get("year"),
                "browseId": sng.get("browseId"),
                "thumbnails": sng.get("thumbnails", [{}])[-1].get("url") if sng.get("thumbnails") else None,
                "type": "Single"
            })

    return {
        "artist": artist["artist"],
        "description": description,
        "image": artist_image,
        "songs": [
            {
                "title": song.get("title"),
                "artist": song.get("artists", [{}])[0].get("name", "Unknown"),
                "album": song.get("album", {}).get("name", "Unknown"),
                "videoId": song.get("videoId"),
                "thumbnails": song.get("thumbnails", [{}])[-1].get("url")
            }
            for song in top_songs_section[:limit]
        ],
        "albums": albums
    }


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
                "videoId": video_id,
                "thumbnails": thumbnail
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
            "videoId": track.get("videoId"),
            "thumbnails": track.get("thumbnails", [{}])[-1].get("url", "")
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

# Function that fetch full album metadata/songs using browseId.
def get_album_tracks(album_browse_id):
    album_data = ytmusic.get_album(album_browse_id)
    if not album_data:
        return None

    album_thumb = None
    if "thumbnails" in album_data and album_data["thumbnails"]:
        album_thumb = album_data["thumbnails"][-1]["url"]

    tracks = []
    for track in album_data.get("tracks", []):
        # Fix thumbnails
        if not track.get("thumbnails"):
            track["thumbnails"] = [{"url": album_thumb}] if album_thumb else []

        # Fix missing/invalid videoId
        if not track.get("videoId"):
            playlist_id = album_data.get("audioPlaylistId")
            track_no = track.get("trackNumber", 0)
            track["videoId"] = f"{playlist_id}#{track_no}"

        tracks.append({
            "title": track.get("title"),
            "artist": track.get("artists", [{}])[0].get("name", "Unknown"),
            "videoId": track.get("videoId"),
            "thumbnails": track["thumbnails"][-1].get("url"),
        })

    return {
        "title": album_data.get("title"),
        "description": album_data.get("description"),
        "tracks": tracks,
    }

# Example Test Run ===
if __name__ == "__main__":
    albums = get_album_tracks('MPREb_tZC7e1H5mfm')
    print(albums['title'])
    for song in albums["tracks"]:
        print(f"{song['title']} - {song['artist']} - {song['videoId']} - {song['thumbnails']}")

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
    artist_info = get_artist_metadata("Rick Astley")
    if artist_info:
        print(f"\nArtist: {artist_info['artist']}")
        print(f"Description: {artist_info['description']}\n")
        print(artist_info["image"])
        print("\nTop Songs:")
        for idx, s in enumerate(artist_info["songs"], start=1):
            print(f"{idx}. {s['title']} - {s['artist']} ({s['album']})")
        print("\nAlbums & Singles:")
        for a in artist_info.get("albums", []):
            print(f"{a['type']}: {a['title']} ({a.get('year', 'Unknown')})")
'''
    '''
    print("\n=== Search Song Example ===")
    song_results = get_song_titles("Blinding Lights")
    if song_results:
        for idx, s in enumerate(song_results, start=1):
            print(f"{idx}. {s['title']} - {s['artist']} ({s['album']}) {s['thumbnails']}")
    '''
    '''
    print("US Charts:", ytmusic.get_charts(country="US"))
    '''
    '''
    genres = get_genres()
    for genre in genres:
        print(f"{genre['title']} {genre['params']}")

    get_genre_songs('ggMPOg1uXzdlSXhKZ0hMV1Z4')
    '''
