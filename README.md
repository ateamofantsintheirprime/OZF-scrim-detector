TO DO LIST:

    1) [x] Hide Private Key in gitignore
        1.1) Add a template file where others can put their private keys if they want to clone the repo
    2) [x] Put it on github.
    3) [x] Add error handling
        (Option 1): Shut down the app when a request fails and give an error message [I went with this one]
        (Option 2): Continue when the error is recieved and handle the missing data (risks hammering the API when I'm getting nothing back but errors)
    4) [] Add individual log requesting and storing
        4.1) [] Decide on directory system for storing individual logs
            (Option 1): A single folder with every log named by their ID.   (nothing wrong with this)
            (Option 2): A logs folder with subfolders for each team, which then contains the logs. (neater)
        4.2) [] Add multithreading
        4.3) [] Add team alignment checking
        
    5) [] Add team alignment checking
    6) [] Add team matchup checking
    7) [] Add test cases (no clue)
    8) [x] Make a config.json file that specifies all filepaths and API URL prefixes, and the season IDs / names they are searching.
    9) [x] Put all the cached API responses in a single filetree, so they arent just floating around in root.
    10) [x] Add that filetree to .gitignore, no point other people downloading the logs themselves. The application is supposed to find the logs pertaining to any arbitrary season.
    11) [] Add checking that the stored files contain valid data, and if not, make the API request and overwrite them.
    12) [x] Restructure datatypes and filetree
    13) [] Replace resources filetree with a proper DB

NOTES: 

- Logs that pass the first round of trimming but not the second round will still be cached. It would be a not insignificant amount of work to avoid this. I wouldn't be able to use the basic make_request() function for it. Probably best to not try avoid it.

- When tackling multiple seasons, the start and end date of the season need to be considered, along side the date that the scrim was played. If a team keeps an identical roster between subsequent seasons, where do you draw the line between the scrims being allocated to the first season's roster or the second season's roster.

- Consider how transfers should be handled? Are they recorded in the ozf API? if 2 core players are transferred out of a roster mid season, then post-transfer logs would not be detected properly

===IMPORTANT IF YOU WANT TO USE THIS PROGRAM YOURSELF===

You will need your own ozfortress API key. I have no idea how to get one, I just asked core on discord and he gave it to me. 

Create a folder called secrets and create a file inside it called ozf_api_key.json and put this in it:
```
{
    "key": <your key as a string>
}
```