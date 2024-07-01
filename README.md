Changes from old design:

- Now uses SQL Alchemy ORM database rather than custom json file tree.

- Although certain data access needs to be done in order (roster must be retrieved from ozf before player logs can be downloaded) 

- Lookup logic now largely uses SQL rather than python code

- Log downloading is totally different

TO DO LIST:

1) Make OZF downloader:
    1.1) Add request re-attempting
    1.2) Check if requested info is already in the league database before checking for a cached response.

2) Learn SQL Alchemy subqueries and other stuff needed for fast database lookups

3) Add test cases:
    3.1) Find a large number (50+ ideally) of known matches between teams manually and add test cases to see if the program can autonomously find them

4) Add more convenient get methods, searching rosters, players etc by name (custom fuzzy search?)

5) Write exponential backoff clock class,  pass in a conditional, success function, and failure function, all as lambda functions. It will then keep its own sleep timer that it updates each time the conditional is checked.

5.5) Use Events to reduce the need for exponential backoff waiting! For example the log processor can wait for a result to be available using an event. And the job dispatcher can wait for a result to be available before moving it to the outer result queue.

6) Add full log downloading

7) Clean up all database code:
    7.1) Write all tables using Column() rather than mapped_column()
    7.2) Move models into their appropriate files.
    7.3) Add class methods to the table objects. e.g. last_and_found = leagues.get_roster("last and found")  and   pengstah = last_and_found.get_player("pengstah") (note, still these methods able to be run without a class instance) 
    7.4) Write functions that can take in multiple input types to be better, with a parameter typed as a union, with checks at the start of the function to see what type the parameter is.
    7.5) Rename database method files.
8) Add custom exceptions for if functions are run in the wrong order.

9) Add write len() function for priority queue class

10) Build UI of some kind!

11) Look into downloading all of the (relevant parts of the) logs.tf database. and store a backup of this, so that it doesn't ever get erased or committed to github. and there's a specific function to access the backup and load logs from it without having to request logs.tf

12) Add robustness so the program can identify and missing info that it needs to support a request and autonomously retrieve required information. For example. if the user asks which teams are  playing in a certain log, the system can notice if it doesn't have a record of a season happening then and looks for one. If it can't find one it looks through the  closest seasons to the date of that log.

13) Identification of off-season scrims

14) Visualiser to compare estimated dates with actual dates for refining estimation methods.
    14.1) Estimated season start and end dates vs what is announced in the season description (manually find)
    14.2) Estimated match windows vs actual match windows. 

15) Date estimation observations: 
   - Swiss matches are usually generated shortly before the week they're played.
   - Match windows in round robin divisions usually line up with match windows in Swiss divisions.
   - Week 4 in round robin prem often (but not always) lines up with week 4 in Swiss inter
   - In Swiss divisions each week will usually have the same maps being played across multiple divisions.

Do an experiment to see if the maps see increased play in the week they are the maps for the official.

NOTES: 

- Consider how transfers should be handled? Are they recorded in the ozf API? if 2 core players are transferred out of a roster mid season, then post-transfer logs would not be detected properly

- How do we handle round robin match gen?

===IMPORTANT IF YOU WANT TO USE THIS PROGRAM YOURSELF===

You will need your own ozfortress API key. I have no idea how to get one, I just asked core on discord and he gave it to me. 

Create a folder called secrets and create a file inside it called ozf_api_key.json and put this in it:
```
{
	"key": <your key as a string>
}
```