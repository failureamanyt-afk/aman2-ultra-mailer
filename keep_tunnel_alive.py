import subprocess
import time
import re
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("Starting AMAN2 Persistent Auto-Reconnecting Cloud Tunnel...")

while True:
    cmd = [
        "ssh",
        "-o", "StrictHostKeyChecking=no",
        "-o", "ServerAliveInterval=15",
        "-o", "ServerAliveCountMax=5",
        "-R", "80:127.0.0.1:5000",
        "serveo.net"
    ]
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in process.stdout:
            print(line, end="", flush=True)
            if "https://" in line:
                urls = re.findall(r'https://[a-zA-Z0-9.-]+\.serveousercontent\.com', line)
                if urls:
                    print(f"\n[ACTIVE GLOBAL LINK] >>> {urls[0]} <<<\n", flush=True)
        process.wait()
    except Exception as e:
        print(f"Tunnel error: {e}", flush=True)
    
    print("Tunnel disconnected. Reconnecting in 3 seconds...", flush=True)
    time.sleep(3)
