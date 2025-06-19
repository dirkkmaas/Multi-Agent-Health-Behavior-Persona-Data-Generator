def extract_window_map(constant_persona_features=None):
    """Extract custom window map if provided in "standard", otherwise use default window map """
    window_map = {}
    # Always use the standard windows, either from constant_persona_features or default
    if constant_persona_features is not None and 'standard' in constant_persona_features:
        for k, v in constant_persona_features['standard'].items():
            window_map[k] = tuple(v)
    else:
        window_map = {
            'morning': (5*60, 12*60),
            'afternoon': (12*60, 18*60),
            'evening': (18*60, 22*60),
            'night': (22*60, 24*60)
        }
    return window_map
