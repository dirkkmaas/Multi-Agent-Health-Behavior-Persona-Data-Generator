from .extract_window_map import extract_window_map
from .get_event_constraints import get_event_constraints
from .parse_ltl_expressions import parse_ltl_expressions
from .compute_event_counts import compute_event_counts
from .build_z3_model_for_day import build_z3_model_for_day
from .extract_spillovers import extract_spillovers
from z3 import sat
import random
import json

def generate_choices_from_distribution(distribution, sample_size):
    """Generate a list of choices according to a distribution and sample size"""
    keys = list(distribution.keys()) # get possibilities for each entry
    percentages = []
    for k in keys:
        percentages.append(distribution[k]) # add percentage for eac hkey
    counts = []
    for p in percentages:
        counts.append(int(round(p * sample_size))) # change this to integer values for person generation
    diff = sample_size - sum(counts) # check if the required sample size is met
    if diff != 0: # if not zero
        max_idx = 0 
        max_val = counts[0]
        for idx, val in enumerate(counts):
            if val > max_val:
                max_val = val
                max_idx = idx
        counts[max_idx] += diff # add the difference to the maximum count
    choices = [] 
    for k, c in zip(keys, counts): # add each possible choice as often as the provided count to the list 
        for _ in range(c):
            choices.append(k)
    random.shuffle(choices) # randomlly shuffle the choices
    return choices

def parse_age_group(age_group_str):
    """For age group get the minimum and maximum age returns random value inbetween them"""
    parts = age_group_str.split('-') # get min and max
    if len(parts) == 2:
        try:
            low = int(parts[0])
            high = int(parts[1])
            return random.randint(low, high) # return random value
        except Exception:
            return None
    return None

def generate_and_analyze_trends(event_definitions, ltl_expressions, constant_persona_features, output_file="multi_person_event_data.json"):
    """"Generate multiple users and create artificial data for them based on the provided event definitions and ltl expressions."""
    sample_size = constant_persona_features.get("sample_size", None) # get sample size
    horizon = constant_persona_features.get("horizon", {}) # duration
    num_weeks = horizon.get("weeks", 4) # get weeks from
    NUM_PERSONS = sample_size # people
    NUM_DAYS = num_weeks * 7 # days

    # Generate personas based on constant_persona_features
    persona_list = []
    # generate the data for dictionaries if not provided, provided unspecified for all.
    gender_choices = generate_choices_from_distribution(constant_persona_features.get("gender", {"unspecified": 1.0}), sample_size)
    edu_choices = generate_choices_from_distribution(constant_persona_features.get("education_level", {"unspecified": 1.0}), sample_size)
    occ_choices = generate_choices_from_distribution(constant_persona_features.get("occupation_status", {"unspecified": 1.0}), sample_size)
    marital_choices = generate_choices_from_distribution(constant_persona_features.get("marital_status", {"unspecified": 1.0}), sample_size)
    field_choices = generate_choices_from_distribution(constant_persona_features.get("field_of_study_distribution", {"unspecified": 1.0}), sample_size)
    housing_choices = generate_choices_from_distribution(constant_persona_features.get("housing_type_distribution", {"unspecified": 1.0}), sample_size)
    for i in range(sample_size):
        persona = {
            "age_group": constant_persona_features["age_group"],
            "age": parse_age_group(constant_persona_features["age_group"]), # get random age from interval
            "gender": gender_choices[i],
            "education_level": edu_choices[i],
            "occupation_status": occ_choices[i],
            "marital_status": marital_choices[i],
            "field_of_study": field_choices[i],
            "housing_type": housing_choices[i],
        }
        persona_list.append(persona)
    random.shuffle(persona_list) # randomly shuffle the personas
    all_persons_data = []
    for person_id in range(NUM_PERSONS): # for each person 
        persona = persona_list[person_id]  # assign persona data
        person_data = {"person_id": person_id, "persona": persona, "days": []} 
        event_counts_per_day = compute_event_counts(event_definitions, NUM_DAYS, seed=person_id, constant_persona_features=constant_persona_features) # compute event counts for the provided num_days (trends etc.)
        spillovers = None
        for day in range(NUM_DAYS):
            fixed_event_counts = event_counts_per_day[day] # extract the fixed event counts for the current day
            solver, event_vars = build_z3_model_for_day(day, NUM_DAYS, event_definitions, ltl_expressions, spillovers, fixed_event_counts, constant_persona_features=constant_persona_features) # build the z3 model
            if solver.check() == sat: # if solved
                model = solver.model()
                spillovers = extract_spillovers(model, event_vars) # get spillovers to use for next day
                day_events = {}
                for t, events in event_vars.items(): # for each event
                    day_events[t] = [] # create a list for the events
                    for i, (s, d) in enumerate(events):
                        s_val = model[s].as_long() # start
                        d_val = model[d].as_long() # duration
                        day_events[t].append({"start": s_val, "duration": d_val})
                person_data["days"].append({"events": day_events, "spillovers": spillovers}) # append spillovers
            else:
                person_data["days"].append({"events": {}, "spillovers": [], "unsat": True}) # if unsat, append to data
        all_persons_data.append(person_data) 
    with open(output_file, "w") as f:
        json.dump(all_persons_data, f, indent=2) # save the data to the output file
    print(f"Generated data for {NUM_PERSONS} persons, {NUM_DAYS} days each, saved to {output_file}")