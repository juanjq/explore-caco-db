import os
import streamlit as st
import re

ICON_FNAME = "icon.png" # In statics folder

import shutil
import os
import streamlit as st

def force_patch():
    st_static_path = os.path.join(os.path.dirname(st.__file__), "static")
    
    MY_ICON = os.path.join(os.path.dirname(__file__), "static", ICON_FNAME)

    # Overwrite the default icons in the library itself
    for target in ["favicon.png", "favicon.ico"]:
        target_path = os.path.join(st_static_path, target)
        try:
            shutil.copy(MY_ICON, target_path)
            print(f"Successfully replaced {target}")
        except Exception as e:
            print(f"Error replacing {target}: {e}")

    print("Default icons replaced. The 'flash' should be gone.")

if __name__ == "__main__":
    force_patch()

