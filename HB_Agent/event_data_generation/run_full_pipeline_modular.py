import os
import shutil
import subprocess
import sys
import json
from event_data_generation.Model_builder.extract_constraints import generate_and_analyze_trends

def get_next_data_folder(base_folder):
    idx = 1
    while os.path.exists(f"{base_folder}/data_{idx}"):
        idx += 1
    return f"{base_folder}/data_{idx}"

def save_used_variables(folder, variables_dict):
    with open(os.path.join(folder, "used_variables.json"), "w") as f:
        json.dump(variables_dict, f, indent=2)

def run_pipeline_from_vars(
    constant_persona_features,
    eventironmental_data,
    ltl_expressions,
    vis_script_folder="Visualization/run.py",
    check_data_folder="Check_data/Run.py",
): #locations for visualization and check data scripts
    username = os.getenv("USERNAME", "default_user")
    base_folder = f"/chroma_db/output_pipeline/{username}"
    output_folder = get_next_data_folder(base_folder) # Output folder
    os.makedirs(output_folder, exist_ok=True)

    variables_runtime_path = os.path.join(output_folder, "Variables_runtime.py") # write variable to python file for later use other files
    with open(variables_runtime_path, "w") as f:
        f.write(f"eventironmental_data = {json.dumps(eventironmental_data, indent=2)}\n")
        f.write(f"ltl_expressions = {json.dumps(ltl_expressions, indent=2)}\n")
        f.write(f"constant_persona_features = {json.dumps(constant_persona_features, indent=2)}\n")

    save_used_variables(output_folder, {
        "constant_persona_features": constant_persona_features,
        "eventironmental_data": eventironmental_data,
        "ltl_expressions": ltl_expressions
    }) # save the variables also as json, for easier access

    print(f"Running data generation, output to {output_folder} ...") # generate the data trough the model
    output_data_file = os.path.join(output_folder, "multi_person_event_data.json")
    generate_and_analyze_trends(eventironmental_data, ltl_expressions, constant_persona_features, output_file=output_data_file)

    # Run the visualization script in the output folder
    print("Running modular visualization...") #
    vis_script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), vis_script_folder))
    subprocess.run([sys.executable, vis_script_path, "multi_person_event_data.json"], check=True, cwd=output_folder)

    # Run the check script in the output folder
    print("Running modular validation pipeline...")
    check_script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), check_data_folder))
    subprocess.run([sys.executable, check_script_path, output_folder], check=True)

    return output_folder 
