import base64
import streamlit as st
from src.config import LOGO_PATH, ICON_PATH

def get_base64(bin_file):
    with open(bin_file, "rb") as f:
        return base64.b64encode(f.read()).decode()

def apply_custom_styles():
    st.set_page_config(page_title="CaCo db query engine", layout="wide", page_icon=ICON_PATH)
    
    st.markdown(f"""
        <style>
            /* Main Layout */
            .stApp {{ background-color: #ffffff; color: #001F54; }}
            
            /* --- SIDEBAR WIDTH & STYLE --- */
            [data-testid="stSidebar"] {{ 
                background-color: #F0F2F6; 
                min-width: 550px !important;
                max-width: 750px !important;
            }}

            /* Sidebar Logo Bar */
            [data-testid="stSidebar"]::before {{
                content: ""; background-image: url("data:image/png;base64,{get_base64(LOGO_PATH)}");
                background-size: contain; background-repeat: no-repeat;
                display: block; width: 80%; height: 100px; margin: 20px auto;
            }}

            header[data-testid="stHeader"] {{ background-color: rgba(0,0,0,0); }}

            /* --- BUTTONS --- */
            div.stButton > button, div.stDownloadButton > button {{ 
                background-color: #003366 !important; color: white !important; border: none !important; 
            }}

            div.stButton > button:active, div.stButton > button:focus,
            div.stDownloadButton > button:active, div.stDownloadButton > button:focus {{ 
                color: #00FFFF !important; background-color: #001F54 !important; box-shadow: 0 0 0 2px #00FFFF !important;
            }}

            /* --- SEGMENTED CONTROL FIX --- */
            div[data-testid="stSegmentedControl"] button[aria-checked="true"] {{
                background-color: #003366 !important; color: white !important;
            }}

            /* --- MULTISELECT CHIPS --- */
            span[data-baseweb="tag"] {{
                background-color: #00FFFF !important; color: #001F54 !important; font-weight: bold;
            }}

            /* --- EXPANDER & INPUT BORDERS --- */
            div[data-testid="stExpander"] {{ border-color: #00FFFF !important; }}
            div[data-baseweb="select"] > div:focus-within, 
            div[data-baseweb="base-input"]:focus-within {{
                border-color: #00FFFF !important; box-shadow: 0 0 0 1px #00FFFF !important;
            }}

            .stMarkdown span[style*="color: #FF4B4B;"] {{ color: #003366 !important; font-weight: bold; }}
        </style>
    """, unsafe_allow_html=True)
