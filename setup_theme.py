import os
import streamlit as st
import re

def brute_force_patch():
    # 1. Find the Streamlit index.html file
    st_static_path = os.path.join(os.path.dirname(st.__file__), "static")
    index_path = os.path.join(st_static_path, "index.html")
    
    if not os.path.exists(index_path):
        print("Could not find index.html")
        return

    with open(index_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 2. Force the favicon link to point to your icon specifically
    # We replace the default favicon.ico reference with a custom one
    new_content = re.sub(
        r'<link rel="shortcut icon" href="[^"]+">',
        f'<link rel="shortcut icon" href="https://raw.githubusercontent.com/FortAwesome/Font-Awesome/6.x/svgs/solid/c.svg">', # Test with a web URL first
        content
    )
    
    # Or replace it with your local file (relative to the static folder)
    # This assumes you have copied iconC.png into that folder already
    new_content = content.replace('favicon.ico', 'icon.png')

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    
    print("index.html has been modified. Please RESTART Streamlit and CLEAR BROWSER CACHE.")

if __name__ == "__main__":
    brute_force_patch()