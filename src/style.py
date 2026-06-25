import base64
import streamlit as st
from src.config import LOGO_PATH, ICON_PATH

def get_base64(bin_file):
    with open(bin_file, "rb") as f:
        return base64.b64encode(f.read()).decode()

def apply_custom_styles():
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

            /* --- TELESCOPE SELECTION ROW --- */
            .telescope-row {{
                position: sticky;
                top: 12px;
                z-index: 90;
                display: grid;
                grid-template-columns: repeat(4, minmax(0, 1fr));
                gap: 0.5rem;
                padding: 0.15rem 0;
                margin-bottom: 0.5rem;
                margin-top: 0.25rem;
                background-color: transparent;
            }}

            .telescope-btn {{
                display: inline-flex;
                justify-content: center;
                align-items: center;
                min-height: 2.6rem;
                padding: 0 0.6rem;
                border-radius: 8px;
                color: #001F54;
                text-decoration: none !important;
                font-weight: 800;
                font-size: 1.05rem;
                line-height: 1.1;
                border: none;
                transition: transform 0.12s ease, box-shadow 0.18s ease, opacity 0.18s ease, border-color 0.18s ease;
            }}

            .telescope-btn:hover {{
                transform: translateY(-1px);
                opacity: 0.98;
                background-color: rgba(0,0,0,0.02);
            }}

            .telescope-btn.selected {{
                color: #001F54;
                box-shadow: none;
                border-bottom: 4px solid currentColor;
                border-top: 4px solid currentColor;
                border-left: 4px solid currentColor;
                border-right: 4px solid currentColor;
                padding-bottom: 0.3rem;
            }}

            .telescope-btn.lst1 {{ background-color: rgba(0,51,102,0.07); color: #003366; }}
            .telescope-btn.lst1.selected {{ color: #003366; background-color: rgba(0,51,102,0.07); }}
            .telescope-btn.lst2 {{ background-color: rgba(35,136,35,0.06); color: #238823; }}
            .telescope-btn.lst2.selected {{ color: #238823; background-color: rgba(35,136,35,0.06); }}
            .telescope-btn.lst3 {{ background-color: rgba(255,127,15,0.06); color: #FF7F0F; }}
            .telescope-btn.lst3.selected {{ color: #FF7F0F; background-color: rgba(255,127,15,0.06); }}
            .telescope-btn.lst4 {{ background-color: rgba(138,43,226,0.06); color: #8A2BE2; }}
            .telescope-btn.lst4.selected {{ color: #8A2BE2; background-color: rgba(138,43,226,0.06); }}

            .stMarkdown span[style*="color: #FF4B4B;"] {{ color: #003366 !important; font-weight: bold; }}
        </style>
    """, unsafe_allow_html=True)
