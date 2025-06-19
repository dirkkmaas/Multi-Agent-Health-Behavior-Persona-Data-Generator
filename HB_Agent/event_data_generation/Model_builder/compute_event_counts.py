import random
from .extract_window_map import extract_window_map
from .get_event_constraints import get_event_constraints


def compute_event_counts(event_definitions, num_days, seed=None, stddev=0.5, constant_persona_features=None):
    """
    Compute a fixed number of events per type per day using trend and randomness.
    """
    if seed is not None:
        random.seed(seed) # if seed is not provided (currently in persona_id)
    window_map = extract_window_map(constant_persona_features) # get window map
    event_counts_per_day = []
    for day_idx in range(num_days): # for day in range number of days
        day_of_week = day_idx % 7 # day of the week integer
        day_name = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'][day_of_week]
        day_counts = {}
        for event_def in event_definitions: # for each event in the event definitions
            event_type = event_def['event_name'] # name
            constraints = get_event_constraints(event_def, day_idx, num_days, window_map, day_name, day_of_week) # get the seasonality constraints
            min_count = constraints['min_count']
            max_count = constraints['max_count']
            base_count = constraints['base_count']
            if base_count <= 0:
                count = 0
            else:
                count = int(round(random.normalvariate(base_count, stddev))) #randomize the generated number
            count = max(min_count, min(max_count, count)) #ensure it is within the bounds
            day_counts[event_type] = count # append the day count for each event type
        event_counts_per_day.append(day_counts) 
    return event_counts_per_day # return the list of number of events per day for each event type
