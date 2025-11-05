import token
from idlelib import query

from dotenv import load_dotenv
from requests import post, get
import json
import os
import base64

load_dotenv()

client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')

def get_token():
    auth_string = client_id + ':' + client_secret
    auth_bytes = auth_string.encode('utf-8')
    auth_base64 = str(base64.b64encode(auth_bytes), 'utf-8')

    url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Authorization': 'Basic ' + auth_base64,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    payload = { 'grant_type': 'client_credentials' }
    result = post(url, headers=headers, data=payload)
    json_data = json.loads(result.content)
    token = json_data['access_token']
    return token

def get_auth_headers(token):
    headers = {
        'Authorization': 'Bearer ' + token,
    }
    return headers

def search_albums(token, album_id):
    url = 'https://api.spotify.com/v1/albums/search'

# Search the artist's name
def search_artists(token, artist_name):
    url = 'https://api.spotify.com/v1/search'
    headers = get_auth_headers(token)

    query = f'?q={artist_name}&type=artist&limit=1'
    query_url = url + query

    response = get(query_url, headers=headers)
    json_data = json.loads(response.content)['artists']['items']

    if len(json_data) == 0: return None

    # print(json.dumps(json_data, indent=4))

    return json_data

# Get the artist songs by its top tracks
def get_artist_songs(token, artist_id):
    url = f'https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US'
    headers = get_auth_headers(token)

    response = get(url, headers=headers)
    json_data = json.loads(response.content)['tracks']

    if len(json_data) == 0: return None

    # print(json.dumps(json_data, indent=4))

    return json_data

# Get the song title and the artist
def get_song_titles(token, song_title):
    url = 'https://api.spotify.com/v1/search'
    headers = get_auth_headers(token)

    query = f'?q=track:{song_title}&type=track'
    query_url = url + query

    response = get(query_url, headers=headers)
    json_data = json.loads(response.content)['tracks']['items']

    if len(json_data) == 0: return None

    # print(json.dumps(json_data, indent=4))

    return [f"{item['name']} -> {item['artists'][0]['name']}" for item in json_data]

user_token = get_token()
'''

artist = search_artists(user_token, 'Rick Astley')
artist_id = artist[0]['id']
songs = get_artist_songs(user_token, artist_id)

for idx, song in enumerate(songs):
    song_name = song['name']
    song_url = song['external_urls']['spotify']

    print(f'{idx + 1}. {song_name}: {song_url}')

'''
song_titles = get_song_titles(user_token, 'Bohemian Rhapsody')

print()
for song in song_titles:
    print(song)
