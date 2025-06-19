import json
import os


def write_summary_report(data_path, persona_results, event_results, seasonal_trend_results, ltl_results_event_model):
    """Write the generated results from the different checks to a summary report file, inputs are the 
    event checks, ltl check and constant persona features check"""
    report_lines = []
    report_lines.append("=== Persona Feature Check ===") # header
    for field, res in persona_results.items():
        if field in ('sample_size', 'horizon'): # skip these fields, are handled in the event constraint section
            continue
        if 'all_match' in res:
            report_lines.append(f"{field}: All match expected value ({res['expected']}): {res['all_match']}")
        else:
            if 'expected' in res:
                is_numeric = True
                for v in res['expected'].values():
                    if not isinstance(v, (float, int)):
                        is_numeric = False
                        break
                if is_numeric:
                    report_lines.append(f"{field}: Distribution (expected vs actual):")
                    actual_counts = res.get('actual_counts', None)
                    for k in set(res['expected']) | set(res['actual']):
                        exp = res['expected'].get(k, 0)
                        act = res['actual'].get(k, 0)
                        count = actual_counts.get(k, 0)
                        report_lines.append(f"  {k}: expected {exp:.2f}, actual {act:.2f}, count {count}")
                else:
                    report_lines.append(f"{field}: Skipped (non-numeric expected values)")
            else:
                if field == 'age_group_check':
                    if 'mismatches' in res and res['mismatches']:
                        report_lines.append("age_group: Some ages are outside their age group bounds:")
                        for mismatch in res['mismatches']:
                            report_lines.append(f"  Person {mismatch['person']}: age {mismatch['age']} not in group {mismatch['age_group']}")
                    elif res.get('all_in_bounds'):
                        avg_age = res.get('average_age', None)
                        if avg_age is not None:
                            report_lines.append(f"age_group: All ages within bounds. Average age: {avg_age:.2f}")
                        else:
                            report_lines.append("age_group: All ages within bounds. Average age: N/A")
                else:
                    report_lines.append(f"{field}: Skipped (no expected values)")
    report_lines.append("")
    report_lines.append("=== Event Constraint Violations ===") # fixed event constraints like min/max counts
    if not event_results:
        report_lines.append("No violations found.")
    else:
        for event_type, violations in event_results.items():
            report_lines.append(f"Event: {event_type}")
            for v in violations:
                if v['type'] == 'per_event_duration': # add for each person and day the violation 
                    report_lines.append(f"  Person {v['person']} Day {v['day']} Event {v['event_idx']}: {', '.join(v['violations'])}")
                else:
                    report_lines.append(f"  Person {v['person']} Day {v['day']}: {', '.join(v['violations'])}")
    report_lines.append("")
    report_lines.append("=== Seasonality/Trend Constraint Check ===")
    data = None # load the data to get the sample size and horizon
    try:
        with open(data_path, 'r') as f:
            data = json.load(f)
    except Exception:
        pass
    if data is not None:
        n_persons = len(data)
        n_days = len(data[0]['days']) if data and 'days' in data[0] else 0
        report_lines.append(f"Actual sample size (counted): {n_persons}")
        report_lines.append(f"Actual horizon (counted): {n_days} days")
    if not seasonal_trend_results:
        report_lines.append("No seasonality/trend constraints found.")
    else:
        for event_type, metrics in seasonal_trend_results.items():
            report_lines.append(f"Event: {event_type}")
            for m in metrics:
                report_lines.append(f"  {m['type']} - {m['desc']}") # add the metrics for each seasonal/trend event
    report_lines.append("")
    report_lines.append("=== LTL (Event Model) Constraint Violations ===")
    if not ltl_results_event_model:
        report_lines.append("No violations found.")
    else:
        for event_type, violations in ltl_results_event_model.items():
            report_lines.append(f"Event(s): {event_type}")
            for v in violations:
                report_lines.append(f"  Person {v['person']} Day {v['day']}: {v['type']} - {v['desc']}") # extract the violations form the results of ltl
    # Write to file
    folder = os.path.dirname(data_path)
    out_path = os.path.join(folder, "summary_report.txt") # write to file
    with open(out_path, 'w', encoding='utf-8') as f:
        for line in report_lines:
            f.write(line + '\n')
    print(f"Summary report written to {out_path}")