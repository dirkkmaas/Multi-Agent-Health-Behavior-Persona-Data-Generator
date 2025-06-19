def get_event_constraints(event_def, day_idx, total_days, window_map, day_name, day_of_week):
    """Get the constraints for an event type on a specific day. Tacking seasonality and trends
    into account. The order of the constraints is important, as it can lead to different results.
    if seasonality is first applied this is added to the base count, this is seen as the normal way of
    operating"""""
    min_count = event_def['temporal_constraints']['total_event_episodes']['min'] 
    max_count = event_def['temporal_constraints']['total_event_episodes']['max']
    base_count = min_count + round((max_count - min_count) / 2) # start at average of both
    base_count_float = float(base_count)
    window_fraction_constraints = []
    allowed_windows = []
    allowed_weekdays = None
    all_windows = set(window_map.keys())
    event_disabled_today = False
    for pattern in event_def['temporal_constraints'].get('temporal_patterns', []):
        mode = pattern['mode']
        details = pattern['details']
        within = details.get('within', None)
        amount = details.get('amount', 0)
        direction = details.get('direction', 'increasing')
        scale = details.get('scale', None)
        if mode == 'fix': # fixed window events
            if isinstance(within, list): # for multiple windows
                for w in within:
                    if w in window_map:
                        allowed_windows.append(w)
            elif isinstance(within, str) and within in window_map: # single window
                allowed_windows.append(within)
        elif mode == 'seasonality':
            if scale == 'weekday':
                if isinstance(within, str): #single day
                    weekdays = [within]
                else:
                    weekdays = within
                weekday_map = {'Monday':0,'Tuesday':1,'Wednesday':2,'Thursday':3,'Friday':4,'Saturday':5,'Sunday':6}
                allowed_indices = []
                for d in weekdays:
                    if d in weekday_map:
                        allowed_indices.append(weekday_map[d]) # add the allowed weekdays that are specified in the constraint
                if amount == 100: # if all for the specified windows
                    if day_of_week not in allowed_indices: # if other day
                        base_count_float = 0 # zero
                        event_disabled_today = True # no events that day
                else:
                    if day_of_week in allowed_indices: # decrease the day amount
                        if direction == 'decreasing':
                            base_count_float *= (1 - amount/100)
                        else: # increase
                            base_count_float *= (1 + amount/100)
            else: # if not in weekday
                is_seasonal = False # flag for weekend seasonality
                is_skip = False
                boosted_windows = []
                if isinstance(within, list): # if multiple windows
                    for day in within:
                        if day in ['Saturday','Sunday','weekend']:
                            if day_of_week in [5, 6]:
                                is_seasonal = True # set to true if the day is seasonal
                            else: 
                                is_skip = True
                    for w in within: # add to boosted windows
                        if w in window_map:
                            boosted_windows.append(w)
                elif isinstance(within, str): # single window
                    if within == 'weekend' and day_of_week in [5, 6]:
                        is_seasonal = True
                    elif within == 'Saturday' and day_of_week == 5:
                        is_seasonal = True
                    elif within == 'Sunday' and day_of_week == 6:
                        is_seasonal = True
                    elif within == 'weekend' and day_of_week in [0, 1, 2, 3, 4]:
                        is_skip = True
                    if within in window_map: # if the window is in the windowmap
                        boosted_windows = [within] # set it as boosted window
                    else:
                        boosted_windows = []
                if is_seasonal: # determine direction of effect
                        if direction == 'decreasing':
                            base_count_float *= (1 - amount/100)
                        else:
                            base_count_float *= (1 + amount/100)
                        continue
                elif is_skip:
                    continue
                else:
                    allowed_windows_set = set(all_windows) # for baseline calcuations
                    baseline_windows = []
                    for w in allowed_windows_set:
                        if w not in boosted_windows:
                            baseline_windows.append(w) # ensure that the baseline is only made from allowed windows
                    n_allowed = len(allowed_windows_set) # allowed windows
                    n_boosted = len(boosted_windows) # boosted windows
                    n_baseline = n_allowed - n_boosted # windows for baseline 
                    if n_allowed > 0 and n_boosted > 0:
                        boost = amount / 100.0
                        if amount == 100:
                            boost_frac = 1.0 / n_boosted
                            for w in boosted_windows:
                                window_fraction_constraints.append((w, boost_frac))
                            for w in baseline_windows:
                                window_fraction_constraints.append((w, 0.0))
                        else:
                            baseline_frac = (1.0 - boost) / n_allowed if n_baseline > 0 else 0.0
                            boost_frac = baseline_frac + boost / n_boosted
                            for w in boosted_windows:
                                window_fraction_constraints.append((w, boost_frac))
                            for w in baseline_windows:
                                window_fraction_constraints.append((w, baseline_frac))
                    elif n_allowed > 0: # if no bosted windows
                        uniform_frac = 1.0 / n_allowed # all the same percentage of events
                        for w in allowed_windows_set: # append to constriants
                            window_fraction_constraints.append((w, uniform_frac))
        elif mode == 'trend': # for trend effects (so long term)
            direction = details.get('direction','') 
            amount = details.get('amount',0)
            trend_start = details.get('start',1) - 1 # -1 to make it zero-indexed
            trend_end = details.get('end',total_days) - 1 # also for zero indexation
            if trend_end > trend_start: # if end day later that start
                trend_days = trend_end - trend_start # number of day
                if day_idx < trend_start: # if not started yet
                    trend_progress = 0.0
                elif day_idx > trend_end: # if already ended
                    trend_progress = 1.0
                else:
                    trend_progress = (day_idx - trend_start) / trend_days # progress of the trend for the specific day
                if direction == 'increasing':
                    base_count_float += trend_progress * amount # increase the base count 
                elif direction == 'decreasing':
                    base_count_float -= trend_progress * amount # decrease the base count
    if allowed_weekdays is not None and day_of_week not in allowed_weekdays: # event disabled 
        base_count_float = 0
        event_disabled_today = True
    if event_disabled_today: # all is zero
        min_count = 0
        max_count = 0
    base_count = int(round(max(min_count, min(max_count, base_count_float)))) # cap the event by its min and max count
    per_event_min = event_def['temporal_constraints']['per_event_duration']['min']
    per_event_max = event_def['temporal_constraints']['per_event_duration']['max']
    per_event_unit = event_def['temporal_constraints']['per_event_duration']['unit']
    if (per_event_unit == 'hours'):  # if the unit is hours, convert to minutes
        per_event_min *= 60
        per_event_max *= 60
    total_min = event_def['temporal_constraints']['total_event_duration']['min']
    total_max = event_def['temporal_constraints']['total_event_duration']['max']
    total_unit = event_def['temporal_constraints']['total_event_duration']['unit']
    if (total_unit == 'hours'): # if the unit is hours, convert to minutes
        total_min *= 60
        total_max *= 60
    if window_fraction_constraints: # loop to ensure that the window fraction constraints never are larger then 1.0
        total_frac = 0
        for w, frac in window_fraction_constraints:
            total_frac += frac
        if total_frac > 1.0:
            new_window_fraction_constraints = []
            for w, frac in window_fraction_constraints:
                new_window_fraction_constraints.append((w, frac/total_frac))# devide by total_frac to normalize back to 1
            window_fraction_constraints = new_window_fraction_constraints
    result = {
        # 'event_name': event_def.get('event_name', 'unknown'),
        'min_count': min_count,
        'max_count': max_count,
        'base_count': base_count,
        'per_event_min': per_event_min,
        'per_event_max': per_event_max,
        'total_min': total_min,
        'total_max': total_max,
        'allowed_windows': allowed_windows,
        'window_fraction_constraints': window_fraction_constraints
    }
    return result