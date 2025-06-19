import json
import sys
import importlib.util
import os
from plots import run_all_plots

if len(sys.argv) > 1:
    INPUT_FILE = sys.argv[1]
else:
    INPUT_FILE = "multi_person_event_data.json"

with open(INPUT_FILE) as f:
    all_results = json.load(f)

# Load custom windows from Variables_runtime.py if available
custom_windows = None
try:
    spec = importlib.util.spec_from_file_location("Variables_runtime", "Variables_runtime.py")
    Variables_runtime = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(Variables_runtime)
    cpf = getattr(Variables_runtime, 'constant_persona_features', None)
    if cpf and 'standard' in cpf:
        custom_windows = {}
        for k, v in cpf['standard'].items():
            custom_windows[k] = tuple(v)
except Exception:
    pass

run_all_plots(all_results, custom_windows)