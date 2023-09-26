import os.path
from config import recent_season_ids, filetree
from Classes import League

# Construct Filetree

for directory in filetree:
    if not os.path.exists(directory):
        os.mkdir(directory)

# Instantiate League objects

league_list = [League(id) for id in recent_season_ids]

# TODO Create analysis documents