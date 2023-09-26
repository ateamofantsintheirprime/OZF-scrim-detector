import os.path, json, requests
from pprint import pprint

def request_batch(cache_filepath_prefix, url_prefix : str, url_ids : list, headers = {}) -> list:
    """ Make multiple requests for different ID's
    from the same URL prefix, return data as a List of JSONObjects
    Store each JSONObject at cache_filepath_prefix/url_id"""
    
    data = []

    # Make sure the cache directory for this batch exists
    if not os.path.exists(cache_filepath_prefix):
        os.mkdir(cache_filepath_prefix)

    for id in url_ids:
        url = url_prefix + str(id)
        filepath = cache_filepath_prefix + str(id)
        data.append(request(filepath, url, headers))
    
    return data

def request(cache_filepath, url, headers = {}):
    """ If the data exists in a file in the cache, then read that file.
    If not, then request that data from the url.
    Take the data from the request, sanitise it and format it.
    Store that data in a file in the cache.
    Return the data as a JSON Object. """
    data = None
        # Check if we already have the requested data stored in the cache
    if os.path.isfile(cache_filepath):
        """ Load the data from the file
        This assumes the file is healthy and accurate
        (probably shouldn't be assumed in the final version)"""
        with open(cache_filepath, 'r') as f:
            print(f"Reading data from cache: {cache_filepath}")
            data = json.loads(f.read().encode("ascii", "ignore"))
            # TODO: Check if file is healthy, if not, then replace it.
    else:
        # Make API request and store it
        print(f"Making request for url: {url}")
        resp = requests.get(url, headers=headers)
        if resp.status_code !=  200:
            print(f"\tWARNING\tError making request, {resp.status_code}")
            return None # Crash the program for now
        # Remove non-ascii characters, thanks bird.
        resp_text = resp.text.encode("ascii", "ignore")
        data = json.loads(resp_text)

        # Write these to the cache.
        with open(cache_filepath, 'w') as f:
            f.write(json.dumps(data, indent=4))
    return data
