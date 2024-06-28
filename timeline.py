# from League_old import *
# from Roster_old import *
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from new_caching_test import update_all_player_logs
# from datetime import datetime, timedelta
from database_helper import construct_league, request_from_ozf, update_all_roster_info, update_all_player_logs
import db

league_data = request_from_ozf(league_id=30)
league = construct_league(json=league_data)

officials = db.get_league_officials(league.id)
update_all_roster_info(league_id=30)

players = db.get_players_in_league(30)

for p in players:
	print(p.name)

rosters = db.get_rosters_in_league(30)

for r in rosters:
	print(f"{r.name}, r_ID:{r.id}")
	
last_and_found_r_id = 1097

update_all_player_logs(30)

logs = db.get_logs_of_roster(1097, 4)
print("lnf logs:")
for log in logs:
	print(log.id)

# Define the main event with start and end dates
# main_event_start = datetime(2023, 1, 1)
# main_event_end = datetime(2023, 12, 31)
main_event_start = league.start_date
main_event_end = league.end_date

sub_events = [
	{
		"name": f"round {match.round_number} gen",
		"start" : match.creation_date,
		"colour" : 'ro'
	} for match in officials
]

# sub_events.extend([
# 	{
# 		"name": f"",
# 		"start" : match.log.date,
# 		"colour" : 'go'
# 	} for match in league.team_matchups
# ])



# pprint(sub_events)

# Create a figure and a set of subplots
fig, ax = plt.subplots(figsize=(10, 6))

# Main event timeline
ax.plot([main_event_start, main_event_end], [1, 1], color='blue', linewidth=3, marker='o', label='Main Event')

# Plot sub-events
for idx, event in enumerate(sub_events, start=2):
	# if 'end' in event:
		# ax.plot([event['start'], event['end']], [idx, idx], color='green', linewidth=2, marker='o')
	# else:
	ax.plot(event['start'], idx, event['colour'])

	# Label the sub-events
	ax.text(event['start'] if 'end' not in event else event['start'] + (event['end'] - event['start']) / 2,
			idx + 0.1, event['name'], verticalalignment='bottom', horizontalalignment='center')

# Format the x-axis
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_minor_locator(mdates.DayLocator(interval=7))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

# Set labels
ax.set_xlabel('Date')
ax.set_ylabel('Events')
ax.set_title('Event Timeline')

# Display grid
ax.grid(True)

# Show legend
ax.legend()

# Show the plot
plt.tight_layout()
plt.show()
