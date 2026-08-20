import os
import zipfile

desktop = r"C:\Users\Friends\Desktop"
src = os.path.join(desktop, "AMAN2_Ultra_Mailer")
zip_out = os.path.join(desktop, "AMAN2_Ultra_Client_Setup.zip")

files = ["app_gui.py", "main.py", "web_server.py", "run.bat", "start_web_server.bat", "README.md", "requirements.txt"]
folders = ["core", "templates"]

with zipfile.ZipFile(zip_out, "w", zipfile.ZIP_DEFLATED) as z:
    for f in files:
        fp = os.path.join(src, f)
        if os.path.exists(fp):
            z.write(fp, arcname=os.path.join("AMAN2_Ultra", f))
    for folder in folders:
        fd = os.path.join(src, folder)
        for root, dirs, fls in os.walk(fd):
            for fl in fls:
                full = os.path.join(root, fl)
                rel = os.path.relpath(full, src)
                z.write(full, arcname=os.path.join("AMAN2_Ultra", rel))

print("Client Commercial Package Created on Desktop:", zip_out)
print("File size:", os.path.getsize(zip_out), "bytes")
