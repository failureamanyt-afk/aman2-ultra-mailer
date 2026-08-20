import os
import zipfile
import shutil

base_dir = r"C:\Users\Friends\.gemini\antigravity\scratch\BM2_Ultra_Mailer"
static_dir = os.path.join(base_dir, "static")
os.makedirs(static_dir, exist_ok=True)
zip_file_path = os.path.join(static_dir, "aman2_ultra_setup.zip")

files_to_include = [
    "app_gui.py",
    "main.py",
    "web_server.py",
    "run.bat",
    "start_web_server.bat",
    "README.md"
]

folders_to_include = [
    "core",
    "templates"
]

with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for f in files_to_include:
        fpath = os.path.join(base_dir, f)
        if os.path.exists(fpath):
            zipf.write(fpath, arcname=os.path.join("AMAN2_Ultra_Mailer", f))
            
    for folder in folders_to_include:
        folder_path = os.path.join(base_dir, folder)
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                full_p = os.path.join(root, file)
                rel_p = os.path.relpath(full_p, base_dir)
                zipf.write(full_p, arcname=os.path.join("AMAN2_Ultra_Mailer", rel_p))

print("Created zip successfully:", os.path.exists(zip_file_path), "Size:", os.path.getsize(zip_file_path))
