import os
import sys
import json
import importlib.util
from Check_constant import check_constant_persona_features
from Check_event import check_event_constraints, check_seasonal_and_trend_constraints
from Check_LTL import check_ltl_constraints_event_model
from Summarize import write_summary_report
import subprocess

def load_data(json_path):
    with open(json_path, 'r') as f:
        return json.load(f)
    
def load_variables_runtime(py_path):
    """Function to load the variables form a data folder as created by the model, for a specific path
    Return the requirested variables, as in the variables_runtime.py file"""
    spec = importlib.util.spec_from_file_location("variables_runtime", py_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["variables_runtime"] = module
    spec.loader.exec_module(module)
    constant_features = getattr(module, 'constant_persona_features', None)
    event_constraints = getattr(module, 'eventironmental_data', None)
    ltl_expressions = getattr(module, 'ltl_expressions', None)
    return constant_features, event_constraints, ltl_expressions

if __name__ == "__main__":
    data_folder = sys.argv[1]
    orig_data_path = os.path.join(data_folder, "multi_person_event_data.json") # for fixed event constraints
    # Use withspillovers for all other checks
    data_path = os.path.join(data_folder, "multi_person_event_data_withspillovers.json")
    variables_py_path = os.path.join(data_folder, "Variables_runtime.py")
    if not os.path.exists(data_path): # function that creates the datset with spillover added to the next day
        if not os.path.exists(orig_data_path):
            print(f"Could not find {orig_data_path}")
            exit(1)
        print("Adding spillover events to next day...")
        spillover_script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "Spillover_correction.py"))
        print(f"[Run.py] Using Spillover_correction.py at: {spillover_script_path}")
        if not os.path.exists(spillover_script_path):
            print(f"ERROR: Spillover_correction.py not found at {spillover_script_path}")
            exit(1)
        result = subprocess.run([
            sys.executable,
            spillover_script_path,
            orig_data_path,
            data_path
        ], capture_output=True, text=True)
    if not os.path.exists(data_path):
        print(f"Could not find {data_path} even after running Spillover_correction.py")
        exit(1)
    if not os.path.exists(variables_py_path):
        print(f"Could not find {variables_py_path}")
        exit(1)
    # Load both datasets
    data_withspill = load_data(data_path) # for checks that require spillover events like ltl constraints
    data_orig = load_data(orig_data_path)
    constant_features, event_constraints, ltl_expressions = load_variables_runtime(variables_py_path) # get variables
    if constant_features is None:
        print("Could not find constant_persona_features in Variables_runtime.py")
        exit(1)
    if event_constraints is None:
        print("Could not find eventironmental_data in Variables_runtime.py")
        exit(1)
    if ltl_expressions is None:
        print("Could not find ltl_expressions in Variables_runtime.py")
        exit(1)
    results = check_constant_persona_features(data_withspill, constant_features) # persona features
    event_results = check_event_constraints(data_orig, event_constraints) # fixed event constraints
    seasonal_trend_results = check_seasonal_and_trend_constraints(data_orig, event_constraints, constant_features) # dynamic checks
    ltl_results_event_model = check_ltl_constraints_event_model(data_withspill, ltl_expressions) # ltl constraints check
    write_summary_report(data_path, results, event_results, seasonal_trend_results, ltl_results_event_model) # report added to data folder