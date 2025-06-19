def parse_ltl_expressions(ltl_expressions):
    """Extract the LTL expressions from the given list and parse them into a structured format."""
    parsed = []
    for expr in ltl_expressions:
        expr = expr.replace('¬', 'not').replace('∧', 'and').replace('→', '->').replace('↔', '<->')
        if expr.startswith('G not(') and 'and' in expr: # no overlap constraint between different events
            inside = expr[len('G not('):-1]  # extract the portion inside the parentheses
            parts = [p.strip() for p in inside.split('and')] # get the two events
            if len(parts) == 2:
                parsed.append({
                    'type': 'no_overlap', 
                    'event_types': (parts[0], parts[1])
                })
                continue
        if expr.startswith('G (') and '-> F (' in expr: # min overlap constraint
            inside = expr[len('G ('):-1]  # remove the outer "G (" and  ")"
            leftPart, rest = inside.split("-> F (", 1) # get leftpart and right
            leftPart = leftPart.strip() # strip both entries from 
            if rest.endswith(')'):
                rest = rest[:-1].strip()  # remove extra trailing ")" if present
            if 'and' in rest:
                inner_parts = [p.strip() for p in rest.split('and')] # get A and B
                if len(inner_parts) == 2 and inner_parts[0] == leftPart: # ensure that the remaining structure is in the shape of A and B
                    parsed.append({
                        'type': 'min_overlap_fraction',
                        'event_types': (leftPart, inner_parts[1]),
                        'min_fraction': 1.0
                    })
                    continue
        if expr.startswith('G (') and '-> F' in expr: # implies future constraint
            inside = expr[len('G ('):-1]
            parts = [p.strip() for p in inside.split('-> F')]
            if len(parts) == 2:
                parsed.append({
                    'type': 'implies_future', 
                    'event_types': (parts[0], parts[1])
                })
                continue

    return parsed
