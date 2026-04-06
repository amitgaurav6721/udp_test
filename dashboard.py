import requests
import urllib3
import time

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://vlts.bihar.gov.in"

def bypass_test():
    # Asli browser headers (Chrome on Windows)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    try:
        # 2-second connect timeout, 5-second read timeout
        r = requests.get(url, headers=headers, timeout=(2, 5), verify=False)
        print(f"[*] SUCCESS! Status: {r.status_code}")
    except requests.exceptions.ConnectTimeout:
        print("[!] Connect Timeout: Firewall is dropping packets.")
    except requests.exceptions.ReadTimeout:
        print("[!] Read Timeout: Server is ignoring the request.")
    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    print("--- BIHAR VLTS STEALTH BYPASS ---")
    while True:
        bypass_test()
        time.sleep(10) # 10 seconds wait taaki firewall ko lage aap human ho
