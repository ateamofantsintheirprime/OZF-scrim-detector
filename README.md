TO DO LIST:

		
	1) [] Add team matchup checking

	2) [] Add test cases (no clue)

	3) [DONE] [check how accurate this estimation is] Get League start and end dates from the that the first and last matches are generated.

	4) [DONE] Add checks to the first round of trimming that the log has the correct number of players. 
		4.1) [NOT DONE] Eventually check the gamemode directly when reading the log individually (how does logs.tf get the gamemode?)

	5) Extricate processes from construction, so that the program can be run with more granularity, and tested more easily (HIGH PRIORITY).
		5.1) E.g. Simply initialising a league doesn't necesarily mean making API requests and initialising all respective teams and players.
		5.2) The entire program shouldn't be run through constructors.
		5.3) You should be able to easily get the logs of just one team. Or some number of teams, or just one player.
	
	6) Check back in on the cursed unicode filtering function

	7) Set up a debug toggle that prints all the detailed info. When this is toggled off just report the data. Maybe set up multiple modes so you can select what data gets printed.

	8) Set up the request_safe backoff time to scale exponentially based on repeated failures (across the whole threadpool) (make each thread wait a random few seconds before starting to request from the api so it doesn't abruptly make 10 requests at once when starting)

	9) Figure out if the resources directory actually is useable for anything

	10) Get info on how much the trimming stage reduces the log list

	11) Break down scrims by team by season and by opponent

	12) Add an expiry date to the cached responses, so the program will periodically go back and "check" that the response hasnt changed

	13) Make it scrape the html for the match comms to see if logs were posted for a more accurate estimate of match dates.

	14) Build a UI

	15) Let people manually input rosters from lists of players or ozf team pages and optional date ranges so they can look at scrim results from preseason / no particular season 

	16) Prioritising logs that are expected to feature multiple teams before the full log is requested from logs.tf

	17) write actual test cases by collecting a bunch of scrim logs between teams and seeing if the program is able to find them (use officials they will be easiest to find)

	18) make it properly record scrim results in json files, with full season breakdowns, team/roster breakdowns and player breakdowns

	19) make it so you can provide any arbitrary log and it will tell u if it's two teams from some ozf season, and if so, which season


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