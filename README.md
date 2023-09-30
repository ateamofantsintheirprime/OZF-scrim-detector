TO DO LIST:

        
    1) [] Add team matchup checking

    2) [] Add test cases (no clue)

    3) [] Get League start and end dates from the that the first and last matches are generated.

    4) [] Add checks to the first round of trimming that the log has the correct number of players. 
        4.1) Eventually check the gamemode directly when reading the log individually

    5) Extricate processes from construction, so that the program can be run with more granularity, and tested more easily.
        5.1) E.g. Simply initialising a league doesn't necesarily mean making API requests and initialising all respective teams and players.
        5.2) The entire program shouldn't be run through constructors.
        5.3) You should be able to easily get the logs of just one team. Or some number of teams, or just one player.
    
    6) Check back in on the cursed unicode filtering function

    7) Set up a debug toggle that prints all the detailed info. When this is toggled off just report the data. Maybe set up multiple modes so you can select what data gets printed.

    8) Set up the request_safe backoff time to scale exponentially based on repeated failures (across the whole threadpool)

NOTES: 

- Consider how transfers should be handled? Are they recorded in the ozf API? if 2 core players are transferred out of a roster mid season, then post-transfer logs would not be detected properly

===IMPORTANT IF YOU WANT TO USE THIS PROGRAM YOURSELF===

You will need your own ozfortress API key. I have no idea how to get one, I just asked core on discord and he gave it to me. 

Create a folder called secrets and create a file inside it called ozf_api_key.json and put this in it:
```
{
    "key": <your key as a string>
}
```