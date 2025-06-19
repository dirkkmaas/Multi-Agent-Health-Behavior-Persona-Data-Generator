import json
import sys
import os
import traceback

def add_spillovers_to_next_day(input_path, output_path=None):
    """Wrapper on orignal dataset to add spillover events to the next day."""
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f) # load the original dataset
    for person in data:
        days = person.get('days', [])
        for day in days:
            events = day.get('events', {})
            for event_type, event_list in events.items():
                for ev in event_list:
                    start = ev.get('start')
                    duration = ev.get('duration')
                    if start is not None and duration is not None and start + duration > 1440:
                        ev['duration'] = max(0, 1440 - start) # set spillover duration to the beginning of the next day for each event
    for person in data:
        days = person.get('days', [])
        for d_idx, day in enumerate(days): # extract index to use for determining the next day
            spillovers = day.get('spillovers', [])
            for spill in spillovers:
                event_type = spill.get('type')
                start = spill.get('start')
                duration = spill.get('duration')
                if start is not None and duration is not None and start + duration > 1440:
                    duration = max(0, 1440 - start) # get the new duration for the spillover
                next_day_idx = d_idx + 1 # get the next day index
                if next_day_idx < len(days) and duration > 0: # if next day exists and duration is larger than 0
                    next_day = days[next_day_idx]
                    if 'events' not in next_day:
                        next_day['events'] = {} # create events dict if not exists
                    if event_type not in next_day['events']:
                        next_day['events'][event_type] = [] # create list for the event type if not exists
                    next_day['events'][event_type].append({'start': start, 'duration': duration}) # append spillover event with start at time 0
    if not output_path:
        output_path = input_path.replace('.json', '_withspillovers.json') # create output path if not provided
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"Spillover events added to next day. Output written to {output_path}")

if __name__ == "__main__":
    try:
        input_path = sys.argv[1]
        output_path = sys.argv[2]
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        add_spillovers_to_next_day(input_path, output_path)
        if not os.path.exists(output_path):
            print(f"[Spillover_correction.py] ERROR: Output file {output_path} was not created!")
            sys.exit(2)
    except Exception as e:
        traceback.print_exc()
        sys.exit(3)
