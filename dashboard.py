import requests
import urllib3
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Bihar Govt Server
url = "https://vlts.bihar.gov.in"

def session_bypass():
    # Session use karne se firewall ko "asli user" ka dhoka hota hai
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,xml;q=0.9,*/*;q=0.8',
        'Upgrade-Insecure-Requests': '1'
    }
    
    try:
        # Pehle home page hit karo session banane ke liye
        print("[*] Attempting Session Handshake...")
        r = session.get(url, headers=headers, timeout=15, verify=False)
        print(f"[*] Success! Status: {r.status_code}")
    except Exception as e:
        print(f"[!] Firewall is still tight: {type(e).__name__}")

if __name__ == "__main__":
    print("--- BIHAR VLTS SESSION BYPASS ---")
    session_bypass()
