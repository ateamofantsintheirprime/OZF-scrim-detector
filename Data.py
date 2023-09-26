import os.path, json, requests
from pprint import pprint

def make_request(filepath, url_prefix : str, url_ids : list, headers = {}) -> list:
    """ If the data exists in a file at filepath, then read that file.
    If not, then request that data from the url.
    Take the data from the request, sanitise it and format it.
    Store that data in a file at filepath.
    Return the data as a List of JSON Objects. """
    
    data = []

    # Check if we already have the requested data stored in filepath
    if os.path.isfile(filepath):
        """ Load the data from the file
        This assumes the file is healthy and accurate
        (probably shouldn't be assumed in the final version)"""
        with open(filepath, 'r') as f:
            print(f"Reading data from file: {filepath}")
            data = json.loads(f.read().encode("ascii", "ignore"))
    else:
        # Make api requests for each url prefix+id pairing
        for id in url_ids:
            url = url_prefix + str(id)
            print(f"Making request for url: {url}")
            # Remove non-ascii characters, thanks bird.
            response_text = requests.get(url, headers=headers).text.encode("ascii", "ignore")
            data.append(json.loads(response_text))

        # Write these to a file.
        with open(filepath, 'w') as f:
            f.write(json.dumps(data, indent=4))
    return data
