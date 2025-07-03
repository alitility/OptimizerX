# modules/ping_test.py

import subprocess
import platform

def ping_test(log_callback=print, host="8.8.8.8", count=4):
    log = log_callback
    log(f"=== Ping Test Starting: {host} ===")
    
    param = "-n" if platform.system().lower()=="windows" else "-c"
    cmd = ["ping", param, str(count), host]
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, universal_newlines=True)
        for line in out.splitlines():
            log(line)
        log("=== Ping Test Completed ===")
    except subprocess.CalledProcessError as e:
        log(f"❌ Ping error: {e}")