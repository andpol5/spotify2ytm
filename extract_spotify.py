import json
from pathlib import Path

import spotipy
from spotipy.oauth2 import SpotifyOAuth
# store your credentials in another file (do not push to Github!)
from .credentials import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URL
CACHE = '.spotipyoauthcache'


def user_saved_tracks_full(spotify_connection):
    """ Get full details of the tracks saved by a user."""

    # first run through also retrieves total no of songs in library
    response = spotify_connection.current_user_saved_tracks(limit=20)
    results = response["items"]

    # subsequently runs until it hits the user-defined limit or has read all songs in the library
    while len(results) < response["total"]:
        response = spotify_connection.current_user_saved_tracks(limit=20, offset=len(results))
        results.extend(response["items"])
    return results


def playlist_tracks_full(spotify_connection, playlist_id=None, fields=None, market=None):
    """ Get full details of the tracks of a playlist owned by a user.
        https://developer.spotify.com/documentation/web-api/reference/playlists/get-playlists-tracks/

        Parameters:
            - user - the id of the user
            - playlist_id - the id of the playlistl
            - fields - which fields to return
            - market - an ISO 3166-1 alpha-2 country code.
    """

    # first run through also retrieves total no of songs in library
    response = spotify_connection.playlist_tracks(playlist_id, fields=fields, limit=100, market=market)
    results = response["items"]

    # subsequently runs until it hits the user-defined limit or has read all songs in the library
    while len(results) < response["total"]:
        response = spotify_connection.playlist_tracks(
            playlist_id, fields=fields, limit=100, offset=len(results), market=market
        )
        results.extend(response["items"])
    return results


def read_liked_songs():
    # Create spotify connection
    out_path = Path('liked_songs.json')
    if out_path.exists():
        with open(out_path) as fh:
            liked_songs = json.load(fh)
        return liked_songs
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="user-library-read",
                        client_id=SPOTIPY_CLIENT_ID,
                        client_secret=SPOTIPY_CLIENT_SECRET,
                        redirect_uri=SPOTIPY_REDIRECT_URL,
                        cache_path=CACHE))

    # Save all "liked songs" into their a single playlist.
    liked_songs = user_saved_tracks_full(sp)
    with open('liked_songs.json', 'w') as fh:
        json.dump(liked_songs, fh)
    return liked_songs

def save_liked_songs_to_playlist():
    liked_songs = read_liked_songs()
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="playlist-modify-private",
                        client_id=SPOTIPY_CLIENT_ID,
                        client_secret=SPOTIPY_CLIENT_SECRET,
                        redirect_uri=SPOTIPY_REDIRECT_URL,
                        cache_path=CACHE))

    user_id = sp.current_user()["id"] # grabs user name
    pl = sp.user_playlist_create(user_id, "Spotify Saved Tracks", public=False, collaborative=False, description="All saved tracks from Spotify")

    track_uris = [track['track']['uri'] for track in liked_songs][::-1]
    for i in range(0, len(track_uris), 100):
        j = min(i + 100, len(track_uris))
        sp.user_playlist_add_tracks(user_id, playlist_id=pl['uri'], tracks=track_uris[i:j])


# save_liked_songs_to_playlist()
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="playlist-read-private",
                     client_id=SPOTIPY_CLIENT_ID,
                     client_secret=SPOTIPY_CLIENT_SECRET,
                     redirect_uri=SPOTIPY_REDIRECT_URL,
                     cache_path=CACHE))

# Get all user playlists
playlists = sp.current_user_playlists()
results = []
for pl in playlists['items']:
    tracks = playlist_tracks_full(sp, pl['id'])
    results.append({'playlist': pl, 'tracks': tracks})

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="playlist-read-collaborative",
                     client_id=SPOTIPY_CLIENT_ID,
                     client_secret=SPOTIPY_CLIENT_SECRET,
                     redirect_uri=SPOTIPY_REDIRECT_URL,
                     cache_path=CACHE))

# Get all user playlists
playlists = sp.current_user_playlists()
for pl in playlists['items']:
    tracks = playlist_tracks_full(sp, pl['id'])
    results.append({'playlist': pl, 'tracks': tracks})


with open('spotify-playlists-me.json', 'w') as fh:
    json.dump(results, fh)
