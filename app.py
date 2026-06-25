import streamlit as st
import os
import base64
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, time

# Custom modules
from src.config import MIN_DATE, DATABASE_NAME, TELESCOPES, DEFAULT_TELESCOPE, ICON_PATH
from src.style import apply_custom_styles
from src.database import get_db, get_mongo_connection_info, get_filtered_collections, fetch_data
from src.processor import process_data_by_var
from src.plot import generate_plot

# Initial page config (must be set before any Streamlit UI calls)
st.set_page_config(page_title="CaCo db query engine", layout="wide", page_icon=ICON_PATH)

SOFT_TELESCOPE_COLORS = {
    "LST1": "#E6F2FF",
    "LST2": "#E8F8E8",
    "LST3": "#FFF4E1",
    "LST4": "#F2E6FF",
}

if "selected_telescope" not in st.session_state:
    st.session_state.selected_telescope = DEFAULT_TELESCOPE

query_params = st.experimental_get_query_params()
selected_telescope = query_params.get("telescope", [st.session_state.selected_telescope])[0]
if selected_telescope not in TELESCOPES:
    selected_telescope = DEFAULT_TELESCOPE
st.session_state.selected_telescope = selected_telescope

# Apply styles and update browser tab title dynamically via JS
apply_custom_styles()
st.markdown(f"<script>document.title = '{selected_telescope} CaCo db query engine';</script>", unsafe_allow_html=True)

# Update favicon dynamically to a telescope-specific placeholder icon (base64 inline)
try:
    base_dir = os.path.dirname(__file__)
    candidate = os.path.join(base_dir, "static", f"icon_{selected_telescope}.png")
    if not os.path.exists(candidate):
        candidate = ICON_PATH
    with open(candidate, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    st.markdown(f"<link rel='icon' href='data:image/png;base64,{b64}' />", unsafe_allow_html=True)
except Exception:
    pass

sidebar_color = SOFT_TELESCOPE_COLORS.get(selected_telescope, "#F0F2F6")
st.markdown(f"<style>[data-testid='stSidebar'] {{ background-color: {sidebar_color}; }}</style>", unsafe_allow_html=True)

button_row = "<div class='telescope-row'>"
for telescope_name in TELESCOPES:
    selected_class = "selected" if telescope_name == selected_telescope else ""
    button_row += (
        f"<a class='telescope-btn {telescope_name.lower()} {selected_class}' "
        f"href='?telescope={telescope_name}'>{telescope_name}</a>"
    )
button_row += "</div>"
st.sidebar.markdown(button_row, unsafe_allow_html=True)

st.title("CaCo db query engine")

# Connection to MongoDB
db = get_db(st.session_state.selected_telescope)
host, port = get_mongo_connection_info(st.session_state.selected_telescope)

# Sidebar setup + selection logic
st.sidebar.header("Query parameters")
filtered_collections = get_filtered_collections(db)
base_collections = sorted(list(set(col.rsplit("_", 1)[0] for col in filtered_collections)))

selected_base = st.sidebar.selectbox("Select collection", options=base_collections)
selected_resolution = st.sidebar.segmented_control("Resolution", options=["min", "hour", "day", "week"], default="min")

selected_col = f"{selected_base}_{selected_resolution}"
if selected_col not in filtered_collections:
    st.sidebar.error(f"Collection '{selected_col}' does not exist in DB.")
    st.stop()

col_ref = db[selected_col]

# Variable selection
try:
    var_list = np.sort(list(col_ref.distinct("name")))
    
    # Style variables multiselect to display in 1 row
    st.markdown("""
    <style>
        div[data-testid='stMultiSelect'] [data-baseweb='tag'] {
            display: inline-flex;
            white-space: nowrap;
        }
        div[data-testid='stMultiSelect'] {
            flex-wrap: nowrap;
            overflow-x: auto;
        }
    </style>
    """, unsafe_allow_html=True)
    
    selected_vars = st.sidebar.multiselect("Select variables", options=var_list, help="Click to add/remove variables")
except Exception as e:
    st.error(f"Error fetching variables: {e}")
    st.stop()

# Time Selection
def parse_manual_time(time_str, default_time):
    try:
        return datetime.strptime(time_str, "%H:%M").time()
    except ValueError:
        # If error, use default
        return default_time

col_top1, col_top2, _, _ = st.sidebar.columns(4)
use_night_preset = col_top1.checkbox("Night-wise", value=False)
use_exact_time = col_top2.checkbox("Detailed time", value=False)

if use_night_preset:
    night_date = st.sidebar.date_input("Night date", value=datetime.now().date(), min_value=MIN_DATE)

    with st.sidebar.expander("Night hours (advanced)", expanded=False):
        night_start_hour = st.number_input("Night start hour (0-23)", min_value=0, max_value=23, value=17)
        night_end_hour = st.number_input("Night end hour (0-23)", min_value=0, max_value=23, value=8)
        start_dt = datetime.combine(night_date, time(hour=night_start_hour))
        end_dt = datetime.combine(night_date + timedelta(days=1 if night_end_hour <= night_start_hour else 0), time(hour=night_end_hour))
else:
    if use_exact_time:

        c1, c2 = st.sidebar.columns([2, 1])
        c3, c4 = st.sidebar.columns([2, 1])
        start_date = c1.date_input("Start date", value=datetime.now() - timedelta(days=7), min_value=MIN_DATE)
        end_date = c3.date_input("End date", value=datetime.now(), min_value=MIN_DATE)
        if use_exact_time:
            t_start = c2.text_input("Start time (HH:MM)", value="00:00")
            t_end = c4.text_input("End time (HH:MM)", value="23:59")
            start_time = parse_manual_time(t_start, time(0, 0))
            end_time = parse_manual_time(t_end, time(23, 59))
        else:
            start_time = time.min
            end_time = time.max
            
        start_dt = datetime.combine(start_date, start_time)
        end_dt = datetime.combine(end_date, end_time)

    else:
        start_date = st.sidebar.date_input("Start time", value=datetime.now() - timedelta(days=7), min_value=MIN_DATE)
        end_date = st.sidebar.date_input("End time", value=datetime.now(), min_value=MIN_DATE)
        start_dt = datetime.combine(start_date, datetime.min.time())
        end_dt = datetime.combine(end_date, datetime.max.time())

show_y_projection = st.sidebar.checkbox("Show Y-axis projection histogram", value=False)

# Plotting
if st.sidebar.button("Fetch data & plot"):
    if not selected_vars:
        st.warning("Please select at least one variable.")
    else:
        all_data = fetch_data(col_ref, selected_vars, start_dt, end_dt)
        
        if not all_data:
            st.warning(f"No data found for {selected_vars} in the selected date range.")
        else:
            # Process data
            data_by_var = process_data_by_var(all_data, selected_vars)
            
            # Display Header
            st.markdown(f"### <span style='color: #00CED1;'>{selected_col}:</span> {', '.join(selected_vars)}", unsafe_allow_html=True)
            
            # Generate  plot
            fig = generate_plot(data_by_var, selected_vars, show_y_projection, use_night_preset, start_dt, end_dt)
            st.plotly_chart(fig, width="stretch")
            
            # Table and download
            all_df = pd.DataFrame(all_data)
            all_df = all_df.drop(columns=["_id", "hierarchical_name"], errors="ignore")
            with st.expander("View raw data table"):
                st.write(all_df.sort_values("date"))
            csv = all_df.to_csv(index=False).encode("utf-8")
            st.download_button(label="Download CSV", data=csv, file_name=f"{selected_col}_{'_'.join(selected_vars)}.csv", mime="text/csv")

st.sidebar.markdown("---")
st.sidebar.caption(f"Connected to MongoDB | {host}:{port} | DB: {DATABASE_NAME}")
st.sidebar.caption("Problems or suggestions: juan.jimenez@ifae.es")