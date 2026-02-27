import os
import streamlit as st
import re

ICON_FNAME = "icon.png" # In statics folder

def force_patch():
    # Find the Streamlit index.html file
    st_static_path = os.path.join(os.path.dirname(st.__file__), "static")
    index_path = os.path.join(st_static_path, "index.html")
    
    if not os.path.exists(index_path):
        print("Could not find index.html")
        return

    with open(index_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Change the favicon link
    # Or replace it with your local file (relative to the static folder)
    for file_format in ["png", "ico"]:
        new_content = content.replace(f"favicon.{file_format}", ICON_FNAME)

        with open(index_path, "w", encoding="utf-8") as f:
            f.write(new_content)
    
    print(f"Modified index.html: {index_path}")
    print("Please RESTART Streamlit and CLEAR BROWSER CACHE.")

if __name__ == "__main__":
    force_patch()

