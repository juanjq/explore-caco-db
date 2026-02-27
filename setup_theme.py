import shutil
import os
import stat
import streamlit as st

ICON_FNAME = "icon.png"

def force_patch():
    # 1. Path to Streamlit's internal static folder
    st_static_path = os.path.join(os.path.dirname(st.__file__), "static")
    
    # 2. Path to your custom icon
    # Using abspath ensures it works regardless of where you call the script from
    base_dir = os.path.dirname(os.path.abspath(__file__))
    MY_ICON = os.path.join(base_dir, "static", ICON_FNAME)

    if not os.path.exists(MY_ICON):
        print(f"ERROR: Cannot find your custom icon at {MY_ICON}")
        return

    # 3. Overwrite the default icons safely
    for target in ["favicon.png", "favicon.ico"]:
        target_path = os.path.join(st_static_path, target)
        try:
            # FIX: If the target exists, we must force-delete it to bypass Conda's read-only lock
            if os.path.exists(target_path):
                # Force add write permissions before deleting, just in case
                os.chmod(target_path, stat.S_IWUSR | stat.S_IREAD) 
                os.remove(target_path)
            
            # Now we can safely copy the new file into the empty slot
            shutil.copy(MY_ICON, target_path)
            print(f"Successfully replaced {target}")
            
        except Exception as e:
            print(f"Error replacing {target}: {e}")

    print("Default icons replaced. The 'flash' should be gone.")

if __name__ == "__main__":
    force_patch()
