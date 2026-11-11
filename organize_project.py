import os
import shutil

# Root directory (current working directory)
base_dir = os.getcwd()

# Define directory mapping
folders = {
    "assets": [],
    "data": [],
    "scripts": [],
    "archive": []
}

# Create folders if they don't exist
for folder in folders.keys():
    os.makedirs(os.path.join(base_dir, folder), exist_ok=True)

# Define file routing rules
for filename in os.listdir(base_dir):
    file_path = os.path.join(base_dir, filename)
    
    # Skip directories and key root files
    if os.path.isdir(file_path) or filename in ["app.py", "organize_project.py", "requirements.txt"]:
        continue

    # File extension and lower name for rule matching
    ext = os.path.splitext(filename)[1].lower()
    lower_name = filename.lower()

    # Route Assets (Logos, palettes, image assets)
    if ext in [".png", ".jpg", ".jpeg", ".pdf", ".psd"] and ("logo" in lower_name or "palette" in lower_name or "assets" in lower_name):
        shutil.move(file_path, os.path.join(base_dir, "assets", filename))
        print(f"Moved to assets/: {filename}")

    # Route Active Data Files (Excel files)
    elif ext in [".xlsx", ".xls", ".csv"] and not lower_name.endswith(".png"):
        if filename == "PV Analysis.xls":
            shutil.move(file_path, os.path.join(base_dir, "archive", filename))
            print(f"Moved to archive/: {filename}")
        else:
            shutil.move(file_path, os.path.join(base_dir, "data", filename))
            print(f"Moved to data/: {filename}")

    # Route Helper Scripts (.py files other than app.py)
    elif ext == ".py":
        shutil.move(file_path, os.path.join(base_dir, "scripts", filename))
        print(f"Moved to scripts/: {filename}")

    # Route Archive/Outputs (.html, static generated chart images)
    elif ext in [".html"] or (ext == ".png" and "chart" in lower_name):
        shutil.move(file_path, os.path.join(base_dir, "archive", filename))
        print(f"Moved to archive/: {filename}")

print("\nProject organization complete!")