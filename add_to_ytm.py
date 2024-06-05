import json
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
from ytmusicapi import YTMusic

ytmusic = YTMusic("oauth.json")

with open('spotify-playlists-me.json') as fh:
    playlists = json.load(fh)

with open('sp2ytm_track_map.json') as fh:
    track_map = json.load(fh)

# All tracks into a big key-value store keyed by spotify track URI.
new_pls = []
for pl in playlists:
    pl2 = {'name': pl['playlist']['name'], 'description': pl['playlist']['description']}
    tracks = [t['track']['uri'] for t in pl['tracks'] if t['track'] is not None]
    tracks = [track_map[uri] for uri in tracks if uri in track_map]
    pl2['tracks'] = tracks
    new_pls.append(pl2)

#time.sleep(3600)

for i, pl in df.iterrows():
    name = str(pl['name'])
    desc = str(pl['description'])
    tracks = eval(pl['tracks'])

    # Send tracks in batches of 500 each
    limit = 500
    count = 0

    try:
        # Let's try to avoid hitting the API limits
        time.sleep(120)
        pl_ytm = ytmusic.create_playlist(pl['name'], pl['description'], 'PRIVATE', tracks[count:min(count + limit, len(tracks))])
        count += limit
        while count < len(tracks):
            ytmusic.add_playlist_items(pl_ytm, tracks[count:min(count + limit, len(tracks))])
            count += limit
            time.sleep(120)
    except:
        print(f'{i} - {name} - failed')

    print(f'{i}/{len(df)}')

# breakpoint to dump you into the interpeter
import bpdb; bpdb.set_trace()
