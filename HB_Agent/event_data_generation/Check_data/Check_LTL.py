def check_ltl_constraints_event_model(data, ltl_expressions):
    """
    Checks LTL constraints as implemented in build_z3_model_for_day
    no_overlap, implies_future, min_overlap_fraction, input is the with spillover data, to ensure that these ltl
    constraints are also respected
    """
    results = {}
    ltl_constraints = [{'formula': expr} for expr in ltl_expressions]
    for p_idx, person in enumerate(data): # iterate over all persons
        for d_idx, day in enumerate(person['days']): # for each day of the specific person
            events = day.get('events', {}) # get the events
            event_instances = []
            for etype, elist in events.items(): # Build a list of all event instances with type, start, duration
                for ev in elist:
                    event_instances.append({'type': etype, 'start': ev.get('start'), 'duration': ev.get('duration')})
            # 1. No overlap for same-type events 
            for etype, elist in events.items():
                if len(elist) == 0: # skip if no events of this type for this day
                    continue
                for i in range(len(elist)): # for each event of this typpe
                    s1 = elist[i].get('start')
                    d1 = elist[i].get('duration')
                    for j in range(i+1, len(elist)): # iterate over all the events
                        s2 = elist[j].get('start')
                        d2 = elist[j].get('duration')
                        if not (s1 + d1 <= s2 or s2 + d2 <= s1): # same logic as constraint applied in build_z3_model_for_day
                            already_reported = any(
                                v['person'] == p_idx and v['day'] == d_idx and v['type'] == 'no_overlap' and v['desc'] == f"Same-type event overlap: {etype} events {i} and {j} overlap | e1: start={s1}, dur={d1}; e2: start={s2}, dur={d2}"
                                for v in results.get(etype, [])
                            ) # check if already reported
                            if not already_reported:
                                s1_str = f"start={s1}, duration={d1}"
                                s2_str = f"start={s2}, duration={d2}"
                                results.setdefault(etype, []).append({
                                    'person': p_idx,
                                    'day': d_idx,
                                    'type': 'no_overlap',
                                    'desc': f"Same-type event overlap: {etype} events {i} and {j} overlap (event {i}: {s1_str}; event {j}: {s2_str})"
                                })
            for ltl in ltl_constraints: # ltl constraints
                formula = ltl.get('formula', '').strip()
                # no_overlap: G ¬(A ∧ B)
                if (formula.startswith('G ¬(') ) and '∧' in formula:
                    inside = formula[formula.find('(')+1:-1]
                    parts = []
                    for p in inside.split('∧'):
                        parts.append(p.strip()) # get the event types
                    if len(parts) == 2:
                        t1, t2 = parts
                        elist1 = events.get(t1, []) # get events
                        elist2 = events.get(t2, [])
                        if len(elist1) == 0 or len(elist2) == 0:
                            continue # if event is disabled due to seasonality constraint, skip
                        for i, ev1 in enumerate(elist1): # use enumerate for later print statement (for clear visualization)
                            s1, d1 = ev1.get('start'), ev1.get('duration') # get start and duration
                            for j, ev2 in enumerate(elist2):
                                s2, d2 = ev2.get('start'), ev2.get('duration')
                                if not (s1 + d1 <= s2 or s2 + d2 <= s1): # same check but now between different event types
                                    results.setdefault(f"{t1},{t2}", []).append({
                                        'person': p_idx,
                                        'day': d_idx,
                                        'type': 'no_overlap',
                                        'desc': f"LTL: {t1} and {t2} overlap (events {i} and {j}) in the same day"
                                    })
                # min_overlap_fraction: G (A → F (A ∧ B))
                elif (formula.startswith('G (')) and ('→ F (' in formula): # ( added to ensure that only the min overlap_faction is used
                    inside = formula[formula.find('(')+1:-1]
                    leftPart, rest = inside.split("→ F (", 1)
                    leftPart = leftPart.strip()
                    if rest.endswith(')'): # ensure that this is dropped
                        rest = rest[:-1].strip()
                    if '∧' in rest: 
                        parts = []
                        for p in rest.split('∧'): 
                            parts.append(p.strip()) # get the two events
                        if len(parts) == 2 and parts[0] == leftPart: # ensure that the shape is respected
                            t1, t2 = leftPart, parts[1]
                            elist1 = events.get(t1, []) # get all events
                            elist2 = events.get(t2, []) # get all second events
                            if len(elist1) == 0 or len(elist2) == 0: # if event is disabled due to seasonality, skip
                                continue
                            for i, ev1 in enumerate(elist1): # for all events A
                                s1 = ev1.get('start')
                                d1 = ev1.get('duration') 
                                overlaps = False
                                for ev2 in elist2: # iterate over all events B 
                                    s2 = ev2.get('start')
                                    d2 = ev2.get('duration')
                                    if s1 < s2 + d2 and s1 + d1 > s2: # same logic as constraint in build_z3_model_for_day if satisfied break
                                        overlaps = True 
                                        break
                                if not overlaps:
                                    s1_str = f"start={s1}, duration={d1}"
                                    if elist2:
                                        t2_events_str = ", ".join([f"start={ev2.get('start')}, duration={ev2.get('duration')}" for ev2 in elist2]) # show all the events of type B in start and duration
                                        t2_events_str = f"[{t2_events_str}]"
                                    else:
                                        t2_events_str = "[none]"
                                    results.setdefault(f"{t1}<->{t2}", []).append({
                                        'person': p_idx,
                                        'day': d_idx,
                                        'type': 'min_overlap_fraction',
                                        'desc': f"min_overlap_fraction violated: {t1} event {i} ({s1_str}) does not overlap any {t2} events: {t2_events_str}"
                                    }) # report violation.
                # implies_future: G (A → F B)
                elif (formula.startswith('G (')) and ('→ F' in formula):
                    if '→ F (' in formula:# skip formulas for min overlap  
                        continue
                    inside = formula[formula.find('(')+1:-1]
                    parts = []
                    for p in inside.split('→ F'):
                        parts.append(p.strip())
                    if len(parts) == 2:
                        t1, t2 = parts
                        elist1 = events.get(t1, [])
                        elist2 = events.get(t2, [])
                        if len(elist1) == 0 or len(elist2) == 0:
                            continue # if event is disabled due to seasonality constraint, skip
                        if elist1 and elist2:
                            latest_t1_end = None
                            for ev in elist1: # for each event of type 1
                                start = ev.get('start', 0)
                                duration = ev.get('duration', 0)
                                if ev.get('start') is not None and ev.get('duration') is not None:
                                    end = start + duration # get the end time
                                    if latest_t1_end is None or end > latest_t1_end:
                                        latest_t1_end = end # the latest end time of event type 1 should be checked
                            latest_t2_start = None
                            for ev in elist2:
                                start = ev.get('start', 0)
                                if ev.get('start') is not None:
                                    if latest_t2_start is None or start > latest_t2_start:
                                        latest_t2_start = start # get the latest start time of event type 2
                            if latest_t2_start < latest_t1_end:  # check if the latest start time of event type 2 is before the latest end time of event type 1
                                results.setdefault(f"{t1}->{t2}", []).append({
                                    'person': p_idx,
                                    'day': d_idx,
                                    'type': 'implies_future',
                                    'desc': f"implies_future violated: latest {t2} does not start at or after latest {t1} ends (latest {t1} end: {latest_t1_end}, latest {t2} start: {latest_t2_start})"
                                })
                        elif elist1 and not elist2:
                            results.setdefault(f"{t1}->{t2}", []).append({
                                'person': p_idx,
                                'day': d_idx,
                                'type': 'implies_future',
                                'desc': f"implies_future violated: {t1} present but no {t2} that day"
                            }) # if event type 1 is present but no event type 2 at all
    return results
