import json
import time
from datetime import datetime
from pathlib import Path

from ytmusicapi import YTMusic

ytmusic = YTMusic("oauth.json")

with open('spotify-playlists-me.json') as fh:
    playlists = json.load(fh)

# All tracks into a big key-value store keyed by spotify track URI.
all_tracks = {}
for pl in playlists:
    for track in pl['tracks']:
        if track['track'] is None:
            continue
        all_tracks[track['track']['uri']] = {
            'name': track['track']['name'],
            'artists': ', '.join([a['name'] for a in track['track']['artists']]),
            'album': track['track']['album']['name'],
        }

ytm_search_results = {}
for i, (suri, s) in enumerate(all_tracks.items()):
    try:
        search_results = ytmusic.search(f"{s['name']} - {s['artists']} - {s['album']}")
        ytm_search_results[suri] = search_results
        time.sleep(1)
    except:
        print(f'{str(datetime.now())} - {i} - failed on {suri} - {s}')
        time.sleep(1)
    if i % 50 == 0:
        print(f'{str(datetime.now())} {i:05d}/{len(all_tracks)}')

with open('youtubemusic-search-results.json', 'w') as fh:
    json.dump(ytm_search_results, fh)
import bpdb; bpdb.set_trace()
