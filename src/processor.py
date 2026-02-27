import numpy as np
from datetime import timedelta

def expand_values_field(docs):
    expanded = []
    for doc in docs:
        if "values" in doc and isinstance(doc["values"], dict):
            base_date = doc.get("date")
            if base_date:
                for second_str, value in doc["values"].items():
                    try:
                        second = int(second_str)
                        new_doc = doc.copy()
                        new_doc["date"] = base_date + timedelta(seconds=second)
                        
                        if isinstance(value, (list, np.ndarray)):
                            arr = np.array(value)
                            array_mean = np.nanmean(arr)
                            new_doc["avg"] = array_mean
                            new_doc["min"] = array_mean
                            new_doc["max"] = array_mean
                            new_doc["is_array_avg"] = len(arr)
                        else:
                            new_doc["avg"] = value
                            new_doc["min"] = value
                            new_doc["max"] = value
                            new_doc["is_array_avg"] = None
                            
                        expanded.append(new_doc)
                    except (ValueError, TypeError):
                        pass
        else:
            expanded.append(doc)
    return expanded

def process_data_by_var(all_data, selected_vars):
    """Groups data by variable and expands the values field."""
    data_by_var = {var: [] for var in selected_vars}
    for doc in all_data:
        var_name = doc.get("name")
        if var_name in data_by_var:
            data_by_var[var_name].append(doc)

    for var in selected_vars:
        data_by_var[var] = expand_values_field(data_by_var[var])
        
    return data_by_var