# --- IMPORTS --- #
import pymongo, base64
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta, time

# MONGO_URI = "mongodb://localhost:27019/"
MONGO_URI = "mongodb://localhost:27018/"
DATABASE_NAME = "CACO"

# Hardcoded parameters --------------
dict_caco_states = {
    0 : "OFF (0)", 1 : "DATA_MONITORING (1)", 2 : "MONITORED (2)", 3 : "SAFE (3)", 4 : "STANDBY (4)",
    5 : "READY (5)", 6 : "OBSERVING (6)", 7 : "TPOINT (7)", 8 : "UNDEFINED (8)", 9 : "TRANSITIONAL (9)", 10 : "ERROR (10)"
}
colors_plots = [
    "#003366", "#00FFFF", "#FF6B00", "rgb(50,205,50)", "rgb(255,165,0)", "rgb(220,20,60)", 
    "rgb(0,206,209)", "rgb(153,51,153)", "rgb(255,215,0)", "rgb(30,144,255)", "rgb(34,139,34)"
]
integer_vars = ["RunNumber"]
fsm_vars = ["CACO_CameraControl_FSM_previous_state", "CACO_CameraControl_FSM_state"]

##################
# --- CONFIG --- #
st.set_page_config(page_title="CaCo db query engine", layout="wide", page_icon="static/icon.png")
st.title("CaCo db query engine")
st.sidebar.header("Query parameters")

LOGO_PATH = "static/ctao_logo.png" 

def get_base64(bin_file):
    with open(bin_file, "rb") as f:
        return base64.b64encode(f.read()).decode()

# CSS for the Top Sidebar Logo and Button interaction
st.markdown(f"""
    <style>
        /* Main Layout */
        .stApp {{ background-color: #ffffff; color: #001F54; }}
        [data-testid="stSidebar"] {{ background-color: #F0F2F6; }}
        /* Sidebar Logo Bar */
        [data-testid="stSidebar"]::before {{
            content: ""; background-image: url("data:image/png;base64,{get_base64(LOGO_PATH)}");
            background-size: contain; background-repeat: no-repeat;
            display: block; width: 80%; height: 100px; margin: 20px auto;
        }}
        header[data-testid="stHeader"] {{ background-color: rgba(0,0,0,0); }}
        /* --- BUTTONS --- */
        /* Forces all buttons to be Navy with White text normally */
        div.stButton > button, div.stDownloadButton > button {{ 
            background-color: #003366 !important; color: white !important; border: none !important; 
        }}
        div.stButton > button:active, div.stButton > button:focus,
        div.stDownloadButton > button:active, div.stDownloadButton > button:focus {{ 
            color: #00FFFF !important; background-color: #001F54 !important; box-shadow: 0 0 0 2px #00FFFF !important;
        }}
        /* --- MULTISELECT CHIPS --- */
        /* Cyan background with Navy letters as requested */
        span[data-baseweb="tag"] {{
            background-color: #00FFFF !important; color: #001F54 !important; font-weight: bold;
        }}
        /* --- EXPANDER & INPUT BORDERS --- */
        div[data-testid="stExpander"] {{ border-color: #00FFFF !important; }}
        div[data-baseweb="select"] > div:focus-within,
        div[data-baseweb="base-input"]:focus-within {{border-color: #00FFFF !important; box-shadow: 0 0 0 1px #00FFFF !important;}}
        .stMarkdown span[style*="color: #FF4B4B;"] {{color: #003366 !important; font-weight: bold;}}
    </style>
""", unsafe_allow_html=True)
##################

# Extract host and port from MONGO_URI #
mongo_host = MONGO_URI.replace("mongodb://", "").replace("/", "")
host, port = mongo_host.split(":") if ":" in mongo_host else (mongo_host, "27017")

# Connection #
@st.cache_resource
def get_client():
    return pymongo.MongoClient(MONGO_URI)
client = get_client()
db = client[DATABASE_NAME]

# Getting collections #
collections = list(db.list_collection_names())
collections.sort(key=lambda x: 
    (0 if x.endswith("_min") else 1 if not any(x.endswith(s) for s in ["_hour", "_day", "_week"]) else 2, x)
)
selected_col = st.sidebar.selectbox("Select collection", options=collections)
col_ref = db[selected_col]

#############################
# --- SELECT VARIABLE/S --- #
try:
    var_list = np.sort(list(col_ref.distinct("name")))
    selected_vars = st.sidebar.multiselect(
    "Select variables", options=var_list, help="Click to add/remove variables to the query"
    )
except Exception as e:
    st.error(f"Error fetching variables: {e}")
    st.stop()
#############################

#######################
# --- SELECT TIME --- #
use_night_preset = st.sidebar.checkbox("Night-wise", value=False)
if use_night_preset:
    night_date = st.sidebar.date_input("Night date", value=datetime.now().date())
    # Advanced hour controls are collapsed by default to keep the sidebar simple
    with st.sidebar.expander("Night hours (advanced)", expanded=False):
        night_start_hour = st.number_input("Night start hour (0-23)", min_value=0, max_value=23, value=17)
        night_end_hour   = st.number_input("Night end hour (0-23)",   min_value=0, max_value=23, value=8)
    # Compute start and end datetimes for the chosen night
    start_dt = datetime.combine(night_date, time(hour=night_start_hour))
    if night_end_hour <= night_start_hour:
        end_dt = datetime.combine(night_date + timedelta(days=1), time(hour=night_end_hour))
    else:
        end_dt = datetime.combine(night_date, time(hour=night_end_hour))
else:
    start_date = st.sidebar.date_input("Start time", value=datetime.now() - timedelta(days=7))
    end_date = st.sidebar.date_input("End time", value=datetime.now())
    start_dt = datetime.combine(start_date, datetime.min.time())
    end_dt = datetime.combine(end_date, datetime.max.time())
#######################

# Optional: show a Y-axis projection histogram on the right
show_y_projection = st.sidebar.checkbox(
    "Show Y-axis projection histogram", value=False, help="Display distribution of plotted Y values to the right"
)

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

#################
# --- QUERY --- #
if st.sidebar.button("Fetch data & plot"):
    if not selected_vars:
        st.warning("Please select at least one variable.")
    else:
        query = {"name": {"$in": selected_vars}, "date": {"$gte": start_dt, "$lte": end_dt}}
        all_data = list(col_ref.find(query).sort("date", 1))
        
        if not all_data:
            st.warning(f"No data found for {selected_vars} in the selected date range.")
        else:
            # Organize data by variable
            data_by_var = {var: [] for var in selected_vars}
            for doc in all_data:
                var_name = doc.get("name")
                if var_name in data_by_var:
                    data_by_var[var_name].append(doc)

            # Expand documents with "values" field into individual datapoints
            for var in selected_vars:
                data_by_var[var] = expand_values_field(data_by_var[var])

            st.markdown(
                f"### <span style='color: #00CED1;'>{selected_col}:</span> {', '.join(selected_vars)}", 
                unsafe_allow_html=True
            )
        
            ####################
            # --- PLOTTING --- #
            if show_y_projection:
                fig = make_subplots(rows=1, cols=2, shared_yaxes=True, column_widths=[0.78, 0.22], specs=[[{"type":"xy"}, {"type":"xy"}]])
            else:
                fig = go.Figure()

            y_values_with_color = []
            for var_idx, (var_name, var_docs) in enumerate(data_by_var.items()):
                if not var_docs:
                    continue
                    
                df = pd.DataFrame(var_docs)
                # ... [your existing df cleaning code] ...

                # --- NEW LEGEND LOGIC ---
                display_name = var_name
                if "is_array_avg" in df.columns:
                    # Get the first non-null size if it exists
                    array_size = df["is_array_avg"].iloc[0] if not df["is_array_avg"].isnull().all() else None
                    if array_size:
                        display_name = f"{var_name} (avg {int(array_size)})"

                color = colors_plots[var_idx % len(colors_plots)]
                
                # ... [Keep your variation check and shaded area logic] ...
                
                # Update the main Scatter trace to use the new display_name
                if show_y_projection:
                    fig.add_trace(go.Scatter(
                        x=df["date"], y=df["avg"], mode="lines+markers", 
                        line_shape="hv", marker=dict(size=6), 
                        name=display_name, # <--- Modified this
                        line=dict(color=color, width=2)
                    ), row=1, col=1)
                else:
                    fig.add_trace(go.Scatter(
                        x=df["date"], y=df["avg"], mode="lines+markers",
                        line_shape="hv", marker=dict(size=6), 
                        name=display_name, # <--- Modified this
                        line=dict(color=color, width=2)
                    ))
            
            # Overlaya mode
            fig.update_layout(
                title_text="", xaxis_title="Time UTC", yaxis_title="Value", hovermode="x unified", 
                height=400, legend=dict(title_text=""), bargap=0.05, barmode="overlay"
            )

            # Histogram projections
            if show_y_projection and y_values_with_color:
                for vals, color, var_name in y_values_with_color:
                    # Using a lower alpha (0.4) ensures visibility of overlaps
                    rgba_color = color.replace("rgb", "rgba").replace(")", ", 0.4)")
                    
                    v_min, v_max = np.min(vals), np.max(vals)
                    v_range = v_max - v_min
                    is_int_var = var_name in integer_vars or var_name in fsm_vars or np.all(np.mod(vals, 1) == 0)

                    if is_int_var:
                        bin_size = 1.0
                        start_val = np.floor(v_min) - 0.5
                        end_val = np.ceil(v_max) + 0.5
                    else:
                        bin_size = (v_range / 40.0) if v_range != 0 else 0.1
                        start_val = v_min
                        end_val = v_max

                    fig.add_trace(go.Histogram(
                        y=vals, orientation="h", ybins=dict(start=start_val, end=end_val, size=bin_size),
                        marker=dict(color=rgba_color, line=dict(color=color, width=1)), 
                        name=f"{var_name} (hist)", showlegend=False, hoverinfo="y+name",
                    ), row=1, col=2)

            # Update Layout
            fig.update_layout(
                title_text="", xaxis_title="Time UTC", yaxis_title="Value",
                hovermode="x unified", height=400, legend=dict(title_text=""), bargap=0.05
            )

            # Y-Axis Logic
            # Case A: FSM State Labels
            if any(var in selected_vars for var in fsm_vars):
                fig.update_layout(yaxis=dict(tickmode="array", tickvals=list(dict_caco_states.keys()), ticktext=list(dict_caco_states.values())))
            
            # Case B: Full Integers
            elif any(var in selected_vars for var in integer_vars):
                fig.update_layout(yaxis=dict(tickformat="d"))

            # If histogram is shown:
            if show_y_projection:
                fig.update_xaxes(showticklabels=False, row=1, col=2)

            # Using the night preset:
            if "use_night_preset" in globals() and use_night_preset:
                try:
                    fig.update_xaxes(range=[start_dt, end_dt])
                except Exception:
                    fig.update_xaxes(range=[start_dt.isoformat(), end_dt.isoformat()])
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show raw data table with all variables
            with st.expander("View raw data table"):
                all_df = pd.DataFrame(all_data)
                if "_id" in all_df.columns:
                    all_df = all_df.drop(columns=["_id"])
                if "hierarchical_name" in all_df.columns:
                    all_df = all_df.drop(columns=["hierarchical_name"])
                st.write(all_df.sort_values("date"))

            # Download Button
            csv = all_df.to_csv(index=False).encode("utf-8")
            st.download_button(label="Download CSV", data=csv, file_name=f"{selected_col}_{"_".join(selected_vars)}.csv", mime="text/csv",)

st.sidebar.markdown("---")
st.sidebar.caption(f"Connected to MongoDB | {host}:{port} | DB: {DATABASE_NAME}")