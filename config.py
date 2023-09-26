from requests.structures import CaseInsensitiveDict
import json
# Could change the directory construction to use os.path.join(folder1, folder2, "")

data_dir                    = "data/"
secrets_directory           = "secrets/" # not included in filetree
resource_directory          = data_dir + "resources/"
cache_directory             = data_dir + "cache/"
leagues_directory           = resource_directory + "leagues/"
logs_directory              = resource_directory + "logs/"
league_response_cache       = cache_directory + "league_data/"
roster_response_cache       = cache_directory + "roster_data/"
player_log_search_cache     = cache_directory + "player_log_search/"
log_cache                   = cache_directory + "logs/"

# The order these directories appear in this list, is the order they are constructed
# Do not change the order.
filetree                    = [data_dir,
                               resource_directory, 
                               leagues_directory, 
                               logs_directory,
                               cache_directory, 
                               league_response_cache,
                               roster_response_cache,
                               player_log_search_cache,
                               log_cache] # To be constructed when program is run

ozf_api_key                 = secrets_directory + "ozf_api_key.json" # This file is ignored by git
ozf_url_prefix              = "https://ozfortress.com/api/v1/"
logs_url_prefix             = "http://logs.tf/api/v1/log"

recent_season_ids           = [56] # These seasons will be searched

headers = CaseInsensitiveDict()
with open(ozf_api_key, "r") as f:
    key = json.loads(f.read())["key"]
headers["X-API-Key"] = key