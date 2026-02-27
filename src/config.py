from datetime import datetime
import os 

# Database port of client + name
MONGO_URI = "mongodb://localhost:27018/"
DATABASE_NAME = "CACO"

# Assets
current_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(current_dir) 
LOGO_PATH = os.path.join(repo_root, "static", "caco_logo.png")
ICON_PATH = os.path.join(repo_root, "static", "icon.png")

# Constants
MIN_DATE = datetime(2000, 1, 1)

DICT_CACO_STATES = {
    0: "OFF (0)", 1: "DATA_MONITORING (1)", 2: "MONITORED (2)", 3: "SAFE (3)", 
    4: "STANDBY (4)", 5: "READY (5)", 6: "OBSERVING (6)", 7: "TPOINT (7)", 
    8: "UNDEFINED (8)", 9: "TRANSITIONAL (9)", 10: "ERROR (10)"
}

COLORS_PLOTS = [
    "rgb(0,51,102)", "rgb(0,255,255)", "rgb(255,107,0)", "rgb(50,205,50)", 
    "rgb(255,165,0)", "rgb(220,20,60)", "rgb(0,206,209)", "rgb(153,51,153)", 
    "rgb(255,215,0)", "rgb(30,144,255)", "rgb(34,139,34)"
]

INTEGER_VARS = ["RunNumber", "EVB_run_number"]

FSM_VARS = ["CACO_CameraControl_FSM_previous_state", "CACO_CameraControl_FSM_state"]

ALLOWED_SUFFIXES = ["_min", "_hour", "_day", "_week"]

# Safety limits
SAFE_QUERY_LIMIT = 40000
