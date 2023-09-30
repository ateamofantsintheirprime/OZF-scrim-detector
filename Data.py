import os.path, json, requests, re
from time import sleep
from concurrent.futures import ThreadPoolExecutor
from pprint import pprint

class RequestFailedError(Exception):
    "Raised when a request fails in a unique way"
    pass
class APIOverloadError(Exception):
    "Raised when a request fails after 10 retries"
    pass

# update this docstring
def request_batch(cache_filepath_prefix, url_prefix : str, url_ids : list, headers = {}) -> list:
    """ Make multiple requests for different IDs
    from the same URL prefix, return data as a List
    Store each element at cache_filepath_prefix/url_id
    
    This function will be parallelised using ThreadPoolExecutor"""
    
    data = []
    results = []
    # Make sure the cache directory for this batch exists
    if not os.path.exists(cache_filepath_prefix):
        os.mkdir(cache_filepath_prefix)

    max_concurrent = 5
    url_list = [url_prefix + id for id in url_ids]
    cache_filepath_list = [cache_filepath_prefix + id + ".json" for id in url_ids]
    headers_list = [headers for i in range(len(url_ids))]
    debug_list = [True for i in range(len(url_ids))]



    with ThreadPoolExecutor(max_concurrent) as executor:
        results = executor.map(request_safe, cache_filepath_list, url_list, headers_list, debug_list)
        re = [r for r in results] #there has to be a better way of doing this
        results = re

    data = [r["data"] for r in results]
    retries = sum([result["attempts"] for result in results])
    print("Batch request complete:")
    print(f"\tJobs: {len(url_list)}")
    print(f"\tNumber of calls needed: {retries}")

    return data

def request_safe(cache_filepath, url, headers = {}, debug = False):
    """This a type of request that "plays nice" with 
    APIs and responds appropriately to their various
    error codes"""
    max_retries = 10 # Most times we can make the same url request before giving up 
    sleep_time = 1 # Amount of time we wait between repeat requests
    # Eventually this should dynamically scale based on how many requests were rejected in a row

    for i in range(max_retries):
        response = request(cache_filepath, url, headers)
        if response["success"]:
            if debug: 
                response["attempts"] = i + 1
                return response
            return response["data"]
        elif response["code"] != 429:
            raise RequestFailedError
        sleep(sleep_time)
        print("Retrying request that got rejected")
    raise APIOverloadError


# UPDate this docstring
def request(cache_filepath, url, headers = {}):
    """ If the data exists in a file in the cache, then read that file.
    If not, then request that data from the url.
    Take the data from the request, sanitise it and format it.
    Store that data in a file in the cache.
    Return the data as a JSON Object."""
    data = None
    code = None
    from_cache = False
        # Check if we already have the requested data stored in the cache
    if os.path.isfile(cache_filepath):
        """ Load the data from the file
        This assumes the file is healthy and accurate
        (probably shouldn't be assumed in the final version)"""
        with open(cache_filepath, 'r') as f:
            # print(f"Reading data from cache: {cache_filepath}")
            data = json.loads(expunge_unicode(f.read()))
            from_cache = True
            # TODO: Check if file is healthy, if not, then replace it.
    else:
        # Make API request
        # print(f"Making request for url: {url}")
        resp = requests.get(url, headers=headers)
        if resp.status_code !=  200:
            print(f"\tWARNING\tError making request, {resp.status_code}")
            return {"success": False, "code" : resp.status_code, "data" : (cache_filepath, url, headers)} # Crash the program for now
            # But return the info needed to attempt the request again
        data = json.loads(expunge_unicode(resp.text))
        code = resp.status_code
        with open(cache_filepath, 'w') as f:
            f.write(json.dumps(data, indent=4))
    return {"success": True, "code": code, "from_cache": from_cache, "data": data}

def expunge_unicode(text):
    """For some reason unicode characters will sometimes
    turn into a 6 character string that consist of the actual
    code. And sometimes they will 'recombine' into the single
    unicode character. We do .encode() to catch cases of the 
    latter, and a regex substitute to catch the former"""
    step_1 = text.encode("ascii", "ignore").decode()
    step_2 = re.sub(r"\\+u\S{4}", "", step_1)
    return step_2