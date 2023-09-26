import os.path, config
from Classes import League

# Construct Filetree

for directory in config.filetree: # if this is the only config asset accessed, just import this
    if not os.path.exists(directory):
        os.mkdir(directory)

# Instantiate League objects

league_list = [League(id) for id in config.recent_season_ids]

# TODO Create analysis documents