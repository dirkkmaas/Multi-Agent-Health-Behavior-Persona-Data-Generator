from collections import Counter

def check_constant_persona_features(data, constant_features):
    """Function to check the person features supplied by the user."""
    results = {}
    persons = data # the different persona data 
    for field, value in constant_features.items():
        if isinstance(value, dict): # if dictionary
            persona_values = [] 
            for p in persons:
                persona_values.append(p['persona'].get(field)) # get the different entries
            counts = Counter() 
            for v in persona_values:
                counts[v] += 1 # count occurence of each specific value (so for example how many persons are single etc)
            total = 0 
            for v in counts.values():
                total += v # get total number over all entries 
            dist = {}
            for k, v in counts.items():
                dist[k] = v / total 
            results[field] = {'expected': value, 'actual': dist, 'actual_counts': dict(counts)} # summarize findings
        elif field == 'age_group':
            # Check that each person's age falls within their age_group
            mismatches = []
            ages_in_bounds = []
            for p_idx, p in enumerate(persons):
                persona = p.get('persona', {})
                age = persona.get('age') # get age
                age_group = persona.get('age_group') # get age group
                if age is not None and age_group is not None:
                    bounds = age_group.split('-')
                    if len(bounds) == 2:
                        lower = int(bounds[0])
                        upper = int(bounds[1]) # extract similar to creation
                        if lower <= age <= upper:
                            ages_in_bounds.append(age) # append age to determine average
                        else:
                            mismatches.append({'person': p_idx, 'age': age, 'age_group': age_group})
            if mismatches:
                results['age_group_check'] = {'mismatches': mismatches} # add mismatches
            else:
                avg_age = sum(ages_in_bounds) / len(ages_in_bounds) # add average age if check correct
                results['age_group_check'] = {'all_in_bounds': True, 'average_age': avg_age}
            
        else:
            continue # other constant persona features are handeled elsewhere
    return results