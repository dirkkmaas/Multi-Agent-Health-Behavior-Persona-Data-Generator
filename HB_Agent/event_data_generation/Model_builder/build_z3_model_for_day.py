from z3 import *
from .extract_window_map import extract_window_map
from .parse_ltl_expressions import parse_ltl_expressions
from .get_event_constraints import get_event_constraints

def build_z3_model_for_day(day_idx, total_days, event_definitions, ltl_expressions=None, spillovers=None, fixed_event_counts=None, constant_persona_features=None):
    """"Function that builds an z3 model for each day that needs to be simulated, use spillover logic from previous day if applicable"""
    solver = Solver() # iniitailize the solver
    event_vars = {}
    window_map = extract_window_map(constant_persona_features) #get the window map
    day_of_week = day_idx % 7 # list of days of the week
    day_name = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'][day_of_week]
    forced_zero_events = set()
    for event_def in event_definitions: # for each event 
        event_type = event_def['event_name']
        constraints = get_event_constraints(event_def, day_idx, total_days, window_map, day_name, day_of_week) # extract the constraints
        per_event_min = constraints['per_event_min']
        per_event_max = constraints['per_event_max']
        total_min = constraints['total_min']
        total_max = constraints['total_max']
        allowed_windows = constraints['allowed_windows']
        window_fraction_constraints = constraints.get('window_fraction_constraints', [])# get the daily dependent window fraction constraints 
        if fixed_event_counts is not None:
            num_events = fixed_event_counts.get(event_type, 0) # get number of events
            if num_events == 0:
                forced_zero_events.add(event_type) # if zero, add to forced zero events for later ltl logic
        else:
            num_events = constraints['base_count'] # if not provided
        if num_events == 0: # for zero logic (as with seasonal events like working)
            event_vars[event_type] = []
            continue
        event_vars[event_type] = []
        if allowed_windows:
            allowed_starts = set()
            for w in allowed_windows:
                if w in window_map:
                    r = window_map[w]
                    allowed_starts.update(range(r[0], r[1], 10)) # create a list of all the allowed starting times for an event provided by windows
        else:
            allowed_starts = set(range(0, 1440, 10)) # if now windows all minutes are allowed
        for i in range(num_events): # for the parsed number of events
            start = Int(f"{event_type}_start_{i}_day{day_idx}") # start integer
            duration = Int(f"{event_type}_duration_{i}_day{day_idx}") # end integer
            event_vars[event_type].append((start, duration)) # add to dictionary
            solver.add(Or([start == t for t in allowed_starts])) # start time must be in previously calculated start times
            solver.add(duration >= per_event_min) # min duration constraint
            solver.add(duration <= per_event_max) # max 
            solver.add(duration > 0) # duration must be longer than zero
            solver.add(duration % 10 == 0) # multiple of 10 min
        solver.add(Sum([ev[1] for ev in event_vars[event_type]]) >= total_min) # loops over all durations to ensure that it is more then min
        solver.add(Sum([ev[1] for ev in event_vars[event_type]]) <= total_max) # loops over all durations to ensure that it is less then max
        for window_name, min_frac in window_fraction_constraints: # window fraction constraints
            if window_name in window_map:
                r = window_map[window_name]
                in_window = [And(ev[0] >= r[0], ev[0] < r[1]) for ev in event_vars[event_type]] # check if the event start time is large then begin window and smaller than end window returns booleans for all events
                solver.add(Sum([If(cond, 1, 0) for cond in in_window]) >= int(min_frac * num_events)) # ensure that sum of booleans is larger than fraction (is rounded down to ensure that problem remains sat)
    for event_type, events in event_vars.items():
        if not events: # if zero events
            continue
        for i in range(len(events)): # ensure that for each event type there is no overlap with its own events
            for j in range(i+1, len(events)):
                s1, d1 = events[i] # start and duration event 1
                s2, d2 = events[j] # start and duration event 2
                solver.add(Or(s1 + d1 <= s2, s2 + d2 <= s1)) # event one ends before start first or second event ends before first starts

    if ltl_expressions is not None:
        parsed_ltl = parse_ltl_expressions(ltl_expressions) # get ltl expressions 
        for expr in parsed_ltl:
            involved_types = set()
            if 'event_types' in expr:
                involved_types.update(expr['event_types'])
            if any(t in forced_zero_events for t in involved_types):
                continue # ensure that events without an entry(so specified zero events are skipped)
            if expr['type'] == 'no_overlap': # no overlap between two events
                t1, t2 = expr['event_types']# get event types
                events1 = event_vars.get(t1, [])
                events2 = event_vars.get(t2, [])
                for i in range(len(events1)):
                    for j in range(len(events2)):
                        s1, d1 = events1[i]
                        s2, d2 = events2[j]
                        solver.add(Or(s1 + d1 <= s2, s2 + d2 <= s1)) # same logic as non overlap with same event types, but now different events
            elif expr['type'] == 'implies_future': # for global constraints
                t1, t2 = expr['event_types']
                events1 = event_vars.get(t1, []) #event A
                events2 = event_vars.get(t2, []) #event B
                for s1, d1 in events1:
                    future_B = [s2 >= s1 + d1 for s2, d2 in events2] # constraint that specifies that the start time of event B must be larger then end time event 1 for all events of type A
                    if future_B:
                        solver.add(Or(future_B))
            elif expr['type'] == 'min_overlap_fraction': # must be an overlap, currently specified as a fraction, might be necessary for later use
                t1, t2 = expr['event_types']
                min_frac = expr['min_fraction'] # default is 1.0, so all events must have one overlap
                events1 = event_vars.get(t1, [])
                events2 = event_vars.get(t2, [])
                overlap_count = []
                for s1, d1 in events1:
                    overlaps = [And(s1 < s2 + d2, s1 + d1 > s2) for s2, d2 in events2] # check if event A overlaps with any event B if the start time of A is smaller then end time of B and end time of A is larger then start time of B
                    overlap_count.append(If(Or(overlaps), 1, 0)) # count with boolean for number of overlaps
                solver.add(Sum(overlap_count) >= int(min_frac * len(events1))) # constraint that checks if the overlap count is satisfied
    if spillovers:
        parsed_ltl = parse_ltl_expressions(ltl_expressions) if ltl_expressions else []
        no_overlap_pairs = set() # get a set to see which pairs of events should not overlap for the spillover
        for expr in parsed_ltl:
            if expr['type'] == 'no_overlap':
                no_overlap_pairs.add(tuple(sorted(expr['event_types'])))
        for spill in spillovers:
            spill_start = spill["start"]
            d_spill = spill["duration"]
            t_spill = spill["type"]
            for t2, events in event_vars.items():
                if not events: # if no events present contintu
                    continue
                if tuple(sorted((t_spill, t2))) in no_overlap_pairs or t2 == t_spill: # check if in no overlap pair or if similar
                    for s2, d2 in events:
                        solver.add(Or(spill_start + d_spill <= s2, s2 + d2 <= spill_start)) # add the no overlap constraint for similar pairs and events that may not overlap with spillover, or are of the same type
    return solver, event_vars
