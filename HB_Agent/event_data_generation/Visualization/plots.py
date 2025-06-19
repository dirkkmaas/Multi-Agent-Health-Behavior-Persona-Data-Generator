import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
import matplotlib.cm as cm
import matplotlib.colors as mcolors

def get_event_counts_by_event_type(data, custom_windows=None):
    """Extract event counts by event type and time windows."""
    WINDOWS = custom_windows if custom_windows is not None else {
        'morning': (5*60, 12*60),
        'afternoon': (12*60, 18*60),
        'evening': (18*60, 22*60),
        'night': (22*60, 24*60)
    }
    DAYS = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    event_counts = {}
    for person in data:
        for day_idx, day in enumerate(person['days']):
            events = day.get('events', {}) # get all the events for the day
            day_of_week = DAYS[day_idx % 7] # determine the day of the week
            for event_type, event_list in events.items():
                if event_type not in event_counts:
                    event_counts[event_type] = {} # add event type to count
                    for w in WINDOWS: 
                        event_counts[event_type][w] = {} # add counts for each event type and window
                        for d in DAYS:
                            event_counts[event_type][w][d] = [] # add count for each event type, window and day
                for event in event_list:
                    start = event.get('start') # get start time of the event
                    for w, (start_min, end_min) in WINDOWS.items(): # get window and start and end time
                        if start and start_min <= start < end_min: # if the start is within the window
                            event_counts[event_type][w][day_of_week].append(1) # append one to the window
    return event_counts, WINDOWS, DAYS

def compute_accumulated_percentages(event_counts, WINDOWS, DAYS):
    """Fucntions to calculate the percentages for each event type per window and per day.
    Uses the dictionary structure from get_event_counts_by_event_type."""
    total_events = {}
    for event_type in event_counts:
        total = 0
        for w in WINDOWS:
            for day in DAYS:
                total += sum(event_counts[event_type][w][day]) #Sums the total for each event type
        total_events[event_type] = total
    # Calculate percentage per window and per day for each event type
    perc_per_window = {}
    perc_per_day = {}
    for event_type in event_counts:
        total = total_events[event_type]
        perc_per_window[event_type] = {} # create a percentage per window for each event
        perc_per_day[event_type] = {} # create a percentage per day for each event
        for w in WINDOWS:
            count = 0
            for day in DAYS:
                count += sum(event_counts[event_type][w][day]) # for each window sum the events over all days
            perc = (count / total * 100) # calculate the percentage in respect to the total
            perc_per_window[event_type][w] = perc # store percentage for each window
        for day in DAYS: #vice versa, now for each day determine the number of days
            count = 0
            for w in WINDOWS:
                count += sum(event_counts[event_type][w][day])
            perc = (count / total * 100) 
            perc_per_day[event_type][day] = perc
    return perc_per_window, perc_per_day

def plot_stacked_bar_percentages(perc_per_window, perc_per_day, WINDOWS, DAYS, output_prefix=None):
    """Creates two plotted stacked bar plots for the percentages of events per window and per day."""
    event_types = list(perc_per_window.keys()) # extract event types from the percentages
    windows = list(WINDOWS.keys()) # extract windows from the percentages
    # Build window_data as a denested explicit for-loop
    window_data = []
    for w in windows:
        row = []
        for e in event_types:
            row.append(perc_per_window[e][w]) # append the percentage for each event type in the specific window to the row
        window_data.append(row)
    fig, ax = plt.subplots(figsize=(10, 6))
    bottom = [0] * len(event_types) # for stacked bar plot
    bar_containers = []
    for i, w in enumerate(windows):
        bars = ax.bar(event_types, window_data[i], bottom=bottom, label=w)
        bar_containers.append(bars)
        bottom = [bottom[j] + window_data[i][j] for j in range(len(event_types))] # reset bottom for the next window
    for i, bars in enumerate(bar_containers):
        for j, bar in enumerate(bars):
            height = bar.get_height()
            if height > 2:
                y = bar.get_y() + height / 2
                ax.text(bar.get_x() + bar.get_width()/2, y, f'{height:.1f}%',
                        ha='center', va='center', color='white', fontsize=9, fontweight='bold')
    ax.set_ylabel('Percentage of Events')
    ax.set_title('Stacked Bar Plot: Percentage of Events per Window (all days)')
    ax.legend(title='Window')
    plt.xticks(rotation=45)
    plt.tight_layout()
    if output_prefix:
        plt.savefig(f'{output_prefix}_window.png')
    plt.close()

    days = DAYS
    day_data = []
    for d in days: # same logic as before but now for days
        row = []
        for e in event_types:
            row.append(perc_per_day[e][d])
        day_data.append(row)
    fig, ax = plt.subplots(figsize=(10, 6))
    bottom = [0] * len(event_types)
    bar_containers = []
    for i, d in enumerate(days):
        bars = ax.bar(event_types, day_data[i], bottom=bottom, label=d)
        bar_containers.append(bars)
        bottom = [bottom[j] + day_data[i][j] for j in range(len(event_types))]
    for i, bars in enumerate(bar_containers):
        for j, bar in enumerate(bars):
            height = bar.get_height()
            if height > 2:
                y = bar.get_y() + height / 2
                ax.text(bar.get_x() + bar.get_width()/2, y, f'{height:.1f}%',
                        ha='center', va='center', color='white', fontsize=9, fontweight='bold')
    ax.set_ylabel('Percentage of Events')
    ax.set_title('Stacked Bar Plot: Percentage of Events per Day of Week (all windows)')
    ax.legend(title='Day')
    plt.xticks(rotation=45)
    plt.tight_layout()
    if output_prefix:
        plt.savefig(f'{output_prefix}_day.png')
    plt.close()

def run_all_plots(all_results, custom_windows=None):
    """Runs all the different plots, outputs events per hour, per day, trend analysis and preview of gantt chart for 
    7 days for one person"""
    persons = all_results
    num_persons = len(persons)
    num_days = len(persons[0]['days'])
    event_types = set()
    for day in persons[0]['days']:
        if 'events' in day:
            event_types.update(day['events'].keys()) #collect all event types from the first person (so will be the same for all persons)
    event_types = list(event_types)
    all_counts = {t: np.zeros((num_days, num_persons)) for t in event_types} # store all counts for each event type, day and person
    for p_idx, person in enumerate(persons):
        for d_idx, day in enumerate(person['days']):
            if 'events' in day:
                for t in event_types:
                    all_counts[t][d_idx, p_idx] = len(day['events'].get(t, [])) # store the number of event for each persons
    avg_counts = {t: np.mean(all_counts[t], axis=1) for t in event_types} # calcualte the average count

    std_counts = {t: np.std(all_counts[t], axis=1) for t in event_types} # calculate the standard deviation 
    plt.figure(figsize=(12, 6))
    for t in event_types:
        plt.plot(range(1, num_days+1), avg_counts[t], label=f"{t} (mean)")
        plt.fill_between(range(1, num_days+1),
                            avg_counts[t] - std_counts[t],
                            avg_counts[t] + std_counts[t],
                            alpha=0.2)
    plt.xlabel("Day")
    plt.ylabel("Average event count per person")
    plt.title(f"Average Event Count per Day Across {num_persons} Persons (Shaded = ±1 std dev)")
    plt.legend()
    plt.tight_layout()
    plt.savefig("trend_analysis_avg_event_count_with_spread.png")
    plt.close()
    print("Trend analysis plot saved as trend_analysis_avg_event_count_with_spread.png")
    # Per-hour-of-day plot (across all persons/days)
    for t in event_types:
        hourly_counts = np.zeros(24)
        total_days = num_days * num_persons # total number of days across all persons
        for p_idx, person in enumerate(persons):
            for day in person['days']:
                if 'events' in day:
                    for ev in day['events'].get(t, []):
                        start_hour = ev['start'] // 60 # convert start time to hour of day
                        hourly_counts[start_hour] += 1 # increment the count for the hour
        avg_hourly = hourly_counts / max(total_days, 1) # avoid division by zero
        plt.figure(figsize=(10, 4))
        plt.bar(range(24), avg_hourly, color='tab:blue')
        plt.xlabel('Hour of Day')
        plt.ylabel('Avg. # Events')
        plt.title(f'Average Number of {t} Events per Hour of Day')
        plt.xticks(range(24))
        plt.tight_layout()
        plt.savefig(f'avg_events_per_hour_{t}.png')
        plt.close()
        print(f"Saved avg events per hour of day for {t} as avg_events_per_hour_{t}.png")
    # Per-weekday plot (mean and stddev across all persons/days)
    for t in event_types:
        weekday_counts = {wd: [] for wd in range(7)}
        for p_idx, person in enumerate(persons):
            for d_idx, day in enumerate(person['days']):
                weekday = d_idx % 7
                if 'events' in day:
                    count = len(day['events'].get(t, []))
                else:
                    count = 0
                weekday_counts[weekday].append(count)
        avg_weekday = np.array([np.mean(weekday_counts[wd]) for wd in range(7)])
        std_weekday = np.array([np.std(weekday_counts[wd]) for wd in range(7)])
        plt.figure(figsize=(8, 4))
        plt.bar(range(7), avg_weekday, color='tab:green', label='Mean')
        plt.errorbar(range(7), avg_weekday, yerr=std_weekday, fmt='none', ecolor='black', capsize=5, label='Std dev')
        plt.xlabel('Weekday')
        plt.ylabel('Average event count per person')
        plt.title(f'Average Number of {t} Events per Weekday (±1 std dev)')
        plt.xticks(range(7), ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'])
        plt.legend()
        plt.tight_layout()
        plt.savefig(f'avg_events_per_weekday_{t}.png')
        plt.close()
        print(f"Saved avg events per weekday for {t} as avg_events_per_weekday_{t}.png")
    # Gantt chart for a single person (first person) and max 7 days
    person = all_results[0]
    days = person['days'][:7] # fix 6 days
    if days and 'events' in days[0]:
        event_types = list(days[0]['events'].keys())
        schedule = []
        for day_idx, day in enumerate(days):
            for et in event_types:
                for idx, ev in enumerate(day['events'][et]):
                    schedule.append({
                        'type': et,
                        'start': ev['start'] + day_idx * 1440,
                        'duration': ev['duration'],
                        'event_num': idx+1,
                        'day': day_idx
                    })
        fig, ax = plt.subplots(figsize=(16, 6))
        yticks = []
        yticklabels = []
        y = 0
        # Dynamically generate a color map based on the number of event types
        n_events = len(event_types)
        # Use a colormap (e.g., tab10, tab20, or hsv) and assign colors to each event type
        cmap = plt.get_cmap('tab20' if n_events > 10 else 'tab10')
        color_list = [mcolors.to_hex(cmap(i % cmap.N)) for i in range(n_events)]
        color_map = {et: color_list[i] for i, et in enumerate(event_types)}
        for et in event_types:
            events = [e for e in schedule if e['type'] == et]
            for ev in events:
                bar_start = ev['start']
                ax.barh(y, ev['duration'], left=bar_start, color=color_map.get(et, 'tab:brown'), edgecolor='black')
                ax.text(bar_start + ev['duration']/2, y, f"{ev['event_num']}", va='center', ha='center', color='white', fontsize=8)
            yticks.append(y)
            yticklabels.append(et)
            y += 1
        ax.set_yticks(yticks)
        ax.set_yticklabels(yticklabels)
        ax.set_xlabel('Time (minutes since start of Day 0)')
        ax.set_title("All Days Event Schedule (First Person, Max 7 Days)")
        for d in range(len(days) + 1):
            ax.axvline(d*1440, color='k', linestyle='--', alpha=0.3)
            ax.text(d*1440 + 10, y-0.5, f"Day {d}", va='top', ha='left', color='k', fontsize=10)
        xticks = []
        xticklabels = []
        for d in range(len(days)):
            for h in range(0, 25, 2):
                xticks.append(d*1440 + h*60)
                xticklabels.append(f"{h:02d}:00\nD{d}")
        ax.set_xticks(xticks)
        ax.set_xticklabels(xticklabels, rotation=45)
        plt.tight_layout()
        plt.savefig("all_days_gantt_singleperson_7days.png")
        plt.close()
        print("All-days Gantt chart (first person, max 7 days) saved as all_days_gantt_singleperson_7days.png")
    # Stacked bar plots logic above
    event_counts, WINDOWS, DAYS = get_event_counts_by_event_type(all_results, custom_windows)
    perc_per_window, perc_per_day = compute_accumulated_percentages(event_counts, WINDOWS, DAYS)
    plot_stacked_bar_percentages(perc_per_window, perc_per_day, WINDOWS, DAYS, output_prefix="event_distribution")
    print("All visualizations complete.")