import requests
import time

# Hum ab Domain use karenge, IP nahi
url = "https://vlts.bihar.gov.in"

def stealth_test():
    try:
        # User-Agent ko bilkul asli browser jaisa rakhein
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
        }
        # SSL Verification bypass karein agar certificate error aaye
        r = requests.get(url, headers=headers, timeout=10, verify=False)
        print(f"[*] Success! Status: {r.status_code}")
    except Exception as e:
        print(f"[!] Still Blocked by Firewall: {e}")

if __name__ == "__main__":
    print("--- BIHAR VLTS EMERGENCY BYPASS ---")
    stealth_test()
