import requests
import urllib3
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://vlts.bihar.gov.in"

# List of Public Proxies (Testing ke liye)
# Agar ye fail ho, toh hum naye proxies dalenge
proxies = {
    "http": "http://43.134.33.12:80", 
    "https": "http://43.134.33.12:80"
}

def proxy_bypass():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/123.0.0.0 Safari/537.36'
    }
    try:
        print(f"[*] Attempting Bypass via Proxy...")
        # Proxy ke saath request bhej rahe hain
        r = requests.get(url, headers=headers, proxies=proxies, timeout=15, verify=False)
        print(f"[*] BYPASS SUCCESS! Status: {r.status_code}")
    except Exception as e:
        print(f"[!] Proxy Blocked or Offline: {type(e).__name__}")

if __name__ == "__main__":
    print("--- BIHAR VLTS PROXY DASHBOARD ---")
    proxy_bypass()
