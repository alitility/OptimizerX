# modules/network_speed.py

import subprocess

def test_speed(log_callback=print):
    log = log_callback

    # Hız testi komutu
    cmd = ["speedtest-cli", "--simple"]

    try:
        out = subprocess.check_output(
            cmd,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        log("=== Speedtest Results ===")
        for line in out.splitlines():
            log(f"{line}")
    except FileNotFoundError:
        log("❌ 'speedtest-cli' command not found!")
        log("   Please install it: pip install speedtest-cli")
    except subprocess.CalledProcessError as e:
        log(f"❌ Speedtest failed: {e.output.strip()}")
    except Exception as e:
        log(f"❌ Unexpected error: {e}")