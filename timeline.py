from League import *
from Roster import *
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta

def draw_timeline(league : League):

    print(type(league.start_date))
    print(league.start_date)
    print(league.end_date)
    pass

league = League(30) 
league.get_officials()

# draw_timeline(league)

# Define the main event with start and end dates
# main_event_start = datetime(2023, 1, 1)
# main_event_end = datetime(2023, 12, 31)
main_event_start = league.start_date
main_event_end = league.end_date

# Define sub-events with either start and end dates, or just a start date
sub_events = [
    {'name': 'Sub-event 1', 'start': datetime(2023, 2, 10), 'end': datetime(2023, 2, 20)},
    {'name': 'Sub-event 2', 'start': datetime(2023, 3, 5), 'end': datetime(2023, 4, 15)},
    {'name': 'Sub-event 3', 'start': datetime(2023, 6, 1), 'end': datetime(2023, 6, 1)},  # Single day event
    {'name': 'Sub-event 4', 'start': datetime(2023, 7, 7)},  # Start date only
    {'name': 'Sub-event 5', 'start': datetime(2023, 10, 1), 'end': datetime(2023, 10, 10)},
]

sub_events = [
    {
        "name": f"round {match['round_number']} gen",
        "start" : datetime.fromisoformat(match["created_at"]).replace(tzinfo=None),
        "colour" : 'ro'
    } for match in league.officials
]

sub_events.extend([
    {
        "name": f"",
        "start" : match.log.date,
        "colour" : 'go'
    } for match in league.team_matchups
])



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
