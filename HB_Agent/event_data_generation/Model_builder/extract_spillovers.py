def extract_spillovers(model, event_vars):
    spillovers = []
    DAY_MINUTES = 1440 # day in minutes
    for t, events in event_vars.items(): # for each event type
        for i, (s, d) in enumerate(events): # for each start and duration
            s_val = model[s].as_long() # start from model
            d_val = model[d].as_long() # duration form model
            if s_val + d_val > DAY_MINUTES: # if the event spills over to the next day
                spillovers.append({
                    "type": t,
                    "start": 0,
                    "duration": (s_val + d_val) - DAY_MINUTES,
                    "orig_start": s_val,
                    "orig_duration": d_val,
                    "event_idx": i
                }) # add as an fixed event for the next day
    return spillovers
