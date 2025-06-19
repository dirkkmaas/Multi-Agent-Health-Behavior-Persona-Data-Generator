import math


def to_minutes(val, unit):
    """Function to convert hour to minutes in constraints"""
    if unit.startswith('hour'):
        return val * 60
    return val


def check_event_constraints(data, event_constraints):
    """
    Checks per-event and per-day constraints for each event type, input is the without spillover json.
    """
    results = {}
    persons = data
    for event in event_constraints: # for each event type extract the constraints
        event_name = event['event_name']
        constraints = event['temporal_constraints']
        per_event_duration = constraints.get('per_event_duration', {})
        total_event_duration = constraints.get('total_event_duration', {})
        total_event_episodes = constraints.get('total_event_episodes', {})
        min_dur = per_event_duration.get('min')
        max_dur = per_event_duration.get('max')
        min_total_dur = total_event_duration.get('min')
        max_total_dur = total_event_duration.get('max')
        min_episodes = total_event_episodes.get('min')
        max_episodes = total_event_episodes.get('max')
        unit = per_event_duration.get('unit', 'minutes')
        # enter all the constraints to ensure that they are in minutes, if already then they are returned as is
        min_dur = to_minutes(min_dur, per_event_duration.get('unit', 'minutes')) if min_dur is not None else None
        max_dur = to_minutes(max_dur, per_event_duration.get('unit', 'minutes')) if max_dur is not None else None
        min_total_dur = to_minutes(min_total_dur, total_event_duration.get('unit', 'minutes')) if min_total_dur is not None else None
        max_total_dur = to_minutes(max_total_dur, total_event_duration.get('unit', 'minutes')) if max_total_dur is not None else None
        allowed_days = None
        patterns = constraints.get('temporal_patterns', [])
        DAYS = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
        for pattern in patterns:
            if pattern.get('mode') == 'seasonality': # if seasonal pattern
                details = pattern.get('details', {})
                within = details.get('within')
                amount = details.get('amount')
                scale = details.get('scale', None)
                if scale == 'weekday' and amount == 100 and isinstance(within, list): # if only enforced on weekdays
                    all_in_days = True
                    for w in within:
                        if w not in DAYS: # to ensure that it is in the list of days
                            all_in_days = False
                            break
                    if all_in_days:
                        allowed_days = set()
                        for w in within:
                            allowed_days.add(DAYS.index(w)) # add the allowed day to the set
        for p_idx in range(len(persons)):
            person = persons[p_idx]
            for d_idx in range(len(person['days'])):
                day = person['days'][d_idx]
                if allowed_days is not None and (d_idx % 7) not in allowed_days:
                    continue # if not allowed in that day, skip
                events = day.get('events', {}).get(event_name, []) # get the events for the current event type
                if len(events) == 0: # if no events, skip
                    continue
                for e_idx in range(len(events)): #for event in events
                    ev = events[e_idx]
                    dur = ev.get('duration') # get duration
                    violations = []
                    if min_dur is not None and dur < min_dur: # min duration check
                        violations.append(f"duration {dur} < min {min_dur}")
                    if max_dur is not None and dur > max_dur: # max duration check
                        violations.append(f"duration {dur} > max {max_dur}")
                    if violations: # add violations to results
                        results.setdefault(event_name, []).append({
                            'person': p_idx, 'day': d_idx, 'event_idx': e_idx, 'type': 'per_event_duration', 'violations': violations
                        })
                total_dur = 0
                for ev in events:
                    dur = ev.get('duration', 0)
                    total_dur += dur # sum up the total duration of all events
                num_episodes = 0
                for _ in events:
                    num_episodes += 1 # event counter
                violations = []
                if min_total_dur is not None and total_dur < min_total_dur:
                    violations.append(f"total duration {total_dur} < min {min_total_dur}") # minimum total duration check
                if max_total_dur is not None and total_dur > max_total_dur:
                    violations.append(f"total duration {total_dur} > max {max_total_dur}") # maximum total duration check
                if min_episodes is not None and num_episodes < min_episodes:
                    violations.append(f"episodes {num_episodes} < min {min_episodes}") # minimum episodes check
                if max_episodes is not None and num_episodes > max_episodes:
                    violations.append(f"episodes {num_episodes} > max {max_episodes}") # maximum episodes check
                if violations:
                    results.setdefault(event_name, []).append({
                        'person': p_idx, 'day': d_idx, 'type': 'per_day', 'violations': violations
                    }) # add violoations to results
    return results

def check_seasonal_and_trend_constraints(data, event_constraints, constant_features=None):
    """
    Checks seasonality and trend constraints for each event type. This is aggregated over 
    all personas and days, due to the randomness implemented in the number of events generation.
    If 'windows' is supplied in constant_persona_features, use those instead of the default.
    """
    # Default windows
    DEFAULT_WINDOWS = {
        'morning': (5*60, 12*60),
        'afternoon': (12*60, 18*60),
        'evening': (18*60, 22*60),
        'night': (22*60, 24*60)
    }
    # Use windows from constant_features if present
    WINDOWS = DEFAULT_WINDOWS
    if constant_features is not None and 'standard' in constant_features:
        try:
            WINDOWS = {}
            for k, v in constant_features['standard'].items():
                WINDOWS[k] = tuple(v) # turn into same structure as DEFAULT_WINDOWS
        except Exception as e:
            print(f"Warning: Could not parse windows from constant_persona_features, using defaults. Error: {e}")
            WINDOWS = DEFAULT_WINDOWS
    DAYS = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    results = {}
    num_persons = len(data) if len(data) > 0 else 1
    for event in event_constraints:
        event_name = event['event_name'] # get all the constant features
        constraints = event['temporal_constraints']
        patterns = constraints.get('temporal_patterns', [])
        all_events = []
        day_events = []
        num_days = 0
        for person in data:
            for d_idx, day in enumerate(person['days']):
                events = day.get('events', {}).get(event_name, [])
                while len(day_events) <= d_idx: # to ensure that if None events are found, the day events gets an empty list, to ensure that the number of days are correct.
                    day_events.append([])
                for ev in events: # add all the events to each day, and total events
                    day_events[d_idx].append(ev)
                    all_events.append(ev)
        num_days = len(day_events) # get number of days
        for pattern in patterns:
            mode = pattern.get('mode')
            details = pattern.get('details', {})
            if mode == 'seasonality':
                within = details.get('within')
                amount = details.get('amount')
                direction = details.get('direction')
                if isinstance(within, list) and all(w in DAYS for w in within): # is within a list and are they all allowed days
                    weekday_indices = []
                    for w in within:
                        if w in DAYS:
                            weekday_indices.append(DAYS.index(w)) # add day to weekday, with indices
                    total_days = len(day_events)
                    days_in_within = 0
                    for i in range(total_days):
                        if i % 7 in weekday_indices: # check if it is an day that is allowed by the window
                            days_in_within += 1
                    days_in_other = total_days - days_in_within # other days vs days in window
                    events_in_within = 0 # event counts for each day that is allowed
                    for i in range(total_days):
                        if i % 7 in weekday_indices:
                            events_in_within += len(day_events[i]) # add all the events
                    events_in_other = 0 # event counts for each day that is not allowed
                    for i in range(total_days):
                        if i % 7 not in weekday_indices:
                            events_in_other += len(day_events[i]) # add all the events
                    num_persons = len(data) if len(data) > 0 else 1
                    avg_events_within = (events_in_within / days_in_within / num_persons) if days_in_within > 0 else 0 # average events in allowed indices per person
                    avg_events_other = (events_in_other / days_in_other / num_persons) if days_in_other > 0 else 0 # average events in other indices per person
                    diff = avg_events_within - avg_events_other # difference between the two
                    # Provide the difference in percentages (relative to avg_events_other)
                    if avg_events_other > 0:
                        diff_pct = 100 * (diff / avg_events_other) # percentage
                    else:
                        diff_pct = float('inf') if avg_events_within > 0 else 0 # if no events in other days, but in within 100 percent case
                    results.setdefault(event_name, []).append({
                        'type': 'seasonality',
                        'desc': f"Avg events per day in {within}: {avg_events_within:.2f}, other days: {avg_events_other:.2f}, diff: {diff:.2f} ({diff_pct:.1f}%), expected diff: {amount}",
                        'actual': diff_pct,
                        'expected': amount,
                        'direction': direction,
                        'window': within,
                        'avg_events_within': avg_events_within,
                        'avg_events_other': avg_events_other,
                        'days_in_within': days_in_within,
                        'days_in_other': days_in_other
                    }) # summarize findings
                else:
                    # Compute expected fractions for all windows (same as get_event_constraints)
                    if amount is not None: 
                        boost = amount / 100.0 
                    else:
                        boost = 0.0
                    if isinstance(within, list): # if multiple windows
                        boosted_windows = []
                        for w in within:
                            if w in WINDOWS:
                                boosted_windows.append(w)
                    elif isinstance(within, str) and within in WINDOWS: # if single window
                        boosted_windows = [within]
                    else:
                        boosted_windows = [] # if no windows are specified
                    allowed_windows_set = set(WINDOWS.keys()) # get all the allowed windows
                    baseline_windows = []
                    for w in allowed_windows_set:
                        if w not in boosted_windows:
                            baseline_windows.append(w) # get the windows for the baseline
                    n_allowed = len(allowed_windows_set) 
                    n_boosted = len(boosted_windows)
                    n_baseline = n_allowed - n_boosted 
                    if n_allowed > 0 and n_boosted > 0:
                        if amount == 100:
                            expected_fractions = {}
                            boost_frac = 1.0 / n_boosted
                            for w in boosted_windows:
                                expected_fractions[w] = boost_frac
                            for w in baseline_windows:
                                expected_fractions[w] = 0.0
                        else:
                            baseline_frac = (1.0 - boost) / n_allowed if n_baseline > 0 else 0.0 # create the baseline fraction based on the remaining percentages 
                            boost_frac = baseline_frac + boost/n_boosted # add boost on top of the baseline ensure that it is corrected for number of boosted windows
                            expected_fractions = {}
                            for w in boosted_windows:
                                expected_fractions[w] = boost_frac
                            for w in baseline_windows:
                                expected_fractions[w] = baseline_frac
                    elif n_allowed > 0: # if all windows allowed, no boost 
                        uniform_frac = 1.0 / n_allowed
                        expected_fractions = {}
                        for w in allowed_windows_set:
                            expected_fractions[w] = uniform_frac
                    else:
                        expected_fractions = {}
                    total_events = len(all_events) # len all event
                    window_counts = {}
                    for w in WINDOWS:
                        window_counts[w] = 0 # initialize the window counts
                    for ev in all_events:
                        start = ev.get('start')
                        for w, (win_start, win_end) in WINDOWS.items(): # loop over the different windows and their start and end times
                            if start is not None and win_start <= start < win_end: # check if she start time is within the window
                                window_counts[w] += 1 # add count
                                break
                    for w in WINDOWS: # for each window, calculate the fraction
                        actual_frac = (window_counts[w] / total_events) if total_events > 0 else 0 # to ensure that this gives no errors
                        expected_frac = expected_fractions.get(w, 0) # get the expected fraction from the dictionary
                        results.setdefault(event_name, []).append({
                            'type': 'seasonality',
                            'desc': f"{w}: {actual_frac*100:.1f}% actual, expected at least {expected_frac*100:.1f}% (events: {window_counts[w]}/{total_events})",
                            'actual': actual_frac*100,
                            'expected': expected_frac*100,
                            'window': w,
                            'window_count': window_counts[w],
                            'total_events': total_events
                        }) # summary
                    count_outside_windows = total_events - sum(window_counts.get(w, 0) for w in WINDOWS) # loop over all the entries in the windows to determine the outside events
                    if count_outside_windows > 0:
                        actual_frac = count_outside_windows / total_events if total_events > 0 else 0 # calculate fraction
                        results.setdefault(event_name, []).append({
                            'type': 'seasonality',
                            'desc': f"Outside defined windows: {actual_frac*100:.1f}% (events: {count_outside_windows}/{total_events})",
                            'actual': actual_frac * 100,
                            'expected': "blank",
                            'window': 'outside',
                            'window_count': count_outside_windows,
                            'total_events': total_events
                        })
            if mode == 'trend': # trend check for each event
                direction = details.get('direction')
                amount = details.get('amount')
                trend_start = details.get('start', 1) - 1 # start day, corrected for zero index
                trend_end = details.get('end', num_days) - 1 # end day, corrected for zero index
                if details.get('scale') == 'season' and trend_end > trend_start: # ensure that the end is larger than the start
                    num_users = len(data) 
                    start_days = [trend_start]
                    end_days = [trend_end]
                    start_events = []
                    end_events = []
                    for d_idx, events in enumerate(day_events):  # for each day and events
                        if d_idx in start_days: # for the d_index in the start days
                            for ev in events:
                                start_events.append(ev) # append all the events to start
                        if d_idx in end_days:
                            for ev in events:
                                end_events.append(ev) # append all events to end
                    avg_start = (len(start_events) / num_users)  # compute the average start events over all the users
                    avg_end = (len(end_events) / num_users)  # compute the average end events over all the users
                    diff = avg_end - avg_start
                    if direction == 'increasing':
                        diff_rounded = math.ceil(diff) # round up if inceasing
                    elif direction == 'decreasing':
                        diff_rounded = math.floor(diff) # round down if decreasing
                    else:
                        diff_rounded = diff
                    results.setdefault(event_name, []).append({
                        'type': 'trend',
                        'desc': f"trend diff {diff_rounded}, expected at least {amount} {direction if direction else ''}",
                        'actual': diff_rounded,
                        'expected': amount,
                        'direction': direction
                    }) # return the results
    return results