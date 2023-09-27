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
        4.2) [] Add multithreaded requests
        
    5) [] Add team alignment checking
    6) [] Add team matchup checking
    7) [] Add test cases (no clue)
    8) [x] Make a config.json file that specifies all filepaths and API URL prefixes, and the season IDs / names they are searching.
    9) [x] Put all the cached API responses in a single filetree, so they arent just floating around in root.
    10) [x] Add that filetree to .gitignore, no point other people downloading the logs themselves. The application is supposed to find the logs pertaining to any arbitrary season.
    11) [] Add checking that the stored files contain valid data, and if not, make the API request and overwrite them.
    12) [x] Restructure datatypes and filetree
    13) [] Replace resources filetree with a proper DB
    14) [] Get League start and end dates from the that the first and last matches are generated. ( THIS IS KIND OF THE SAME AS 16)
        [Note] Sometimes all regular season matches are generated at the start of the league (round robin), and sometimes they are generated week by week. Thankfully Grand-finals are always generated immediately prior to the final week of the season.
        14.1) Different divisions end at different times, make sure we take the date of the latest Grand-finals.
    15) [] Add checking to the first round of trimming that the log has the correct number of players
    16) Calculate the probably start and end dates of each season.
        16.a1) Start Date = The creation date of the first match to be created (minus 1/2 weeks to be generous)
        16.a2) End Date = The creation date of the last grand-finals match to be generated. (plus 2ish weeks to give space for the match to be played)
        NOTE: CONSIDER IF ANY PROBLEMS WOULD ARISE SHOULD 2 OR MORE SEASONS OVERLAP!

        16.b1) Start Date = The midpoint between the generation date round 1 of the first season, and 1 week after the generation date of the final round of the prior season. This also is equal to the End date of the prior Season.

        16.c1) Some extremely cursed natural language processing on the description text of the season, which contains a semi-colloquial explanation of the schedule of the season.


    17) Add a intermediary round of trimming based on the dates using **BINARY SEARCH (maybe)**.
        17.1) Eliminate logs with a date preceeding the start of the season.
        17.2) Eliminate logs with an date succeeding the end of the season.
        17.3) This probably will be fast enough that binary search is not needed. but might be good to add to the shopping list eventually.
    
    18) Add a script that looks through the last like 20 leagues and sees if any of them have overlap in match dates, if not maybe we can just assume that it won't happen (doubtful).

NOTES: 

- ALL API responses are cached, regardless of whether or not they contain any information that is used by the program. Not really a simple or neccessary 'problem' to fix. Only solution I can think of is to delete irrelevant API caches, and then add them to a 'blacklist' so the program remembers that the data is irrelevant and doesn't request it again.

- When tackling multiple seasons, the start and end date of the season need to be considered, along side the date that the scrim was played. If a team keeps an identical roster between subsequent seasons, where do you draw the line between the scrims being allocated to the first season's roster or the second season's roster.

- Consider how transfers should be handled? Are they recorded in the ozf API? if 2 core players are transferred out of a roster mid season, then post-transfer logs would not be detected properly

- Consider how to calculate start and end dates for seasons. What about when seasons overlap? Two 6s seasons will never overlap and the same goes for two highlander seasons. But you may find a team that is signed up for a 6s season, and a very similar but distinct (3-5 players in common) team that is playing in a simultaneously running 6s cup.  

- It would be really nice if the dates of each league start and end, along with the date that match scores were submitted, was accessible in the API. 

===IMPORTANT IF YOU WANT TO USE THIS PROGRAM YOURSELF===

You will need your own ozfortress API key. I have no idea how to get one, I just asked core on discord and he gave it to me. 

Create a folder called secrets and create a file inside it called ozf_api_key.json and put this in it:
```
{
    "key": <your key as a string>
}
```