import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from src.config import COLORS_PLOTS, INTEGER_VARS, FSM_VARS, DICT_CACO_STATES

def generate_plot(data_by_var, selected_vars, show_y_projection, use_night_preset, start_dt, end_dt):
    if show_y_projection:
        fig = make_subplots(rows=1, cols=2, shared_yaxes=True, 
                            column_widths=[0.78, 0.22], specs=[[{"type":"xy"}, {"type":"xy"}]])
    else:
        fig = go.Figure()

    y_values_with_color = []
    
    for var_idx, (var_name, var_docs) in enumerate(data_by_var.items()):
        if not var_docs:
            continue
            
        df = pd.DataFrame(var_docs)

        display_name = var_name
        if "is_array_avg" in df.columns:
            array_size = df["is_array_avg"].iloc[0] if not df["is_array_avg"].isnull().all() else None
            if array_size:
                display_name = f"{var_name} (avg {int(array_size)})"

        color = COLORS_PLOTS[var_idx % len(COLORS_PLOTS)]
        
        if color.startswith('#'):
            c_hex = color.lstrip('#')
            r, g, b = tuple(int(c_hex[i:i+2], 16) for i in (0, 2, 4))
            rgba_color = f"rgba({r},{g},{b},0.2)"
        else:
            rgba_color = color.replace("rgb", "rgba").replace(")", ", 0.2)")

        show_band = "min" in df.columns and "max" in df.columns and (df["min"] != df["max"]).any()
        
        if show_y_projection:
            y_values_with_color.append((df["avg"].values, color, var_name))
        
        col_idx = 1 if show_y_projection else None

        if show_band:
            fig.add_trace(go.Scatter(x=df["date"], y=df["max"], mode="lines", line=dict(width=0, shape="hv"), showlegend=False, hoverinfo="skip"), row=1 if show_y_projection else None, col=col_idx)
            fig.add_trace(go.Scatter(x=df["date"], y=df["min"], mode="lines", fill="tonexty", fillcolor=rgba_color, line=dict(width=0, shape="hv"), showlegend=False, hoverinfo="skip"), row=1 if show_y_projection else None, col=col_idx)
        
        fig.add_trace(go.Scatter(
            x=df["date"], y=df["avg"], mode="lines+markers", 
            line_shape="hv", marker=dict(size=6),  
            name=display_name, 
            line=dict(color=color, width=2)
        ), row=1 if show_y_projection else None, col=col_idx)

    # Layout updates
    fig.update_layout(
        title_text="", xaxis_title="Time UTC", yaxis_title="Value", hovermode="x unified",  
        height=400, legend=dict(title_text=""), bargap=0.05, barmode="overlay"
    )

    # Histogram projections
    if show_y_projection and y_values_with_color:
        for vals, color, var_name in y_values_with_color:
            rgba_color_hist = color.replace("rgb", "rgba").replace(")", ", 0.4)")
            v_min, v_max = np.min(vals), np.max(vals)
            v_range = v_max - v_min
            is_int_var = var_name in INTEGER_VARS or var_name in FSM_VARS or np.all(np.mod(vals, 1) == 0)

            if is_int_var:
                bin_size, start_val, end_val = 1.0, np.floor(v_min) - 0.5, np.ceil(v_max) + 0.5
            else:
                bin_size, start_val, end_val = (v_range / 40.0) if v_range != 0 else 0.1, v_min, v_max

            fig.add_trace(go.Histogram(
                y=vals, orientation="h", ybins=dict(start=start_val, end=end_val, size=bin_size),
                marker=dict(color=rgba_color_hist, line=dict(color=color, width=1)),  
                name=f"{var_name} (hist)", showlegend=False, hoverinfo="y+name",
            ), row=1, col=2)
            
        fig.update_xaxes(showticklabels=False, row=1, col=2)

    # Y-Axis Logic
    if any(var in selected_vars for var in FSM_VARS):
        fig.update_layout(yaxis=dict(tickmode="array", tickvals=list(DICT_CACO_STATES.keys()), ticktext=list(DICT_CACO_STATES.values())))
    elif any(var in selected_vars for var in INTEGER_VARS):
        fig.update_layout(yaxis=dict(tickformat="d"))

    if use_night_preset:
        try:
            fig.update_xaxes(range=[start_dt, end_dt])
        except Exception:
            fig.update_xaxes(range=[start_dt.isoformat(), end_dt.isoformat()])

    return fig