import subprocess
import time
import re
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("=" * 65)
print("AMAN2 - Universal Public Link Generator for Friends")
print("=" * 65)
print("\nConnecting to Global Tunnel to generate your Live HTTPS Link...")

cmd = ["ssh", "-o", "StrictHostKeyChecking=no", "-o", "ServerAliveInterval=30", "-R", "80:127.0.0.1:5000", "serveo.net"]

try:
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    for line in process.stdout:
        print(line, end="")
        if "https://" in line:
            urls = re.findall(r'https://[a-zA-Z0-9.-]+\.serveousercontent\.com', line)
            if urls:
                public_url = urls[0]
                print("\n" + "=" * 65)
                print("🌟 YOUR UNIVERSAL PUBLIC LINK FOR FRIENDS (ANY PC / MOBILE):")
                print(f"👉 Main Portal:   {public_url}")
                print(f"👉 Download Page: {public_url}/download")
                print(f"👉 Login Page:    {public_url}/login")
                print("=" * 65 + "\n")
                print("Keep this window open to keep the link active for your friends!")
except Exception as e:
    print("Error:", e)
