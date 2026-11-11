import os
import shutil
from datetime import datetime

def make_project_backup():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_folder = f"project_backup_{timestamp}"
    
    os.makedirs(backup_folder, exist_ok=True)
    
    # Core application files to backup
    files_to_backup = ["app.py", "clean_data.py", "requirements.txt"]
    for file in files_to_backup:
        if os.path.exists(file):
            shutil.copy2(file, os.path.join(backup_folder, file))
            print(f"📦 Backed up: {file}")
            
    # Directories to backup
    dirs_to_backup = ["data", "assets"]
    for d in dirs_to_backup:
        if os.path.exists(d):
            shutil.copytree(d, os.path.join(backup_folder, d))
            print(f"📁 Backed up directory: {d}/")
            
    print(f"\n🎉 Successfully created full project snapshot in: '{backup_folder}'")

if __name__ == "__main__":
    make_project_backup()