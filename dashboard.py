import requests
import time
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://vlts.bihar.gov.in"

def stealth_test():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
    }
    try:
        print(f"[*] Testing connection to {url}...")
        # IPv4 force karne ke liye (if possible)
        r = requests.get(url, headers=headers, timeout=15, verify=False)
        print(f"[*] Success! Status: {r.status_code}")
    except Exception as e:
        print(f"[!] Blocked/Timeout: {e}")

if __name__ == "__main__":
    print("--- BIHAR VLTS DASHBOARD ---")
    stealth_test()
