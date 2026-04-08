import streamlit as st
import socket
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os

# --- Page Setup ---
st.set_page_config(page_title="GATLING NITRO V89", page_icon="🚀", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #050505; color: #00FF00; }
    div.stButton > button {
        background-color: #004400; color: white; border-radius: 8px; font-weight: bold; width: 100%; height: 3.5em;
    }
    .stMetric { background-color: #111; padding: 15px; border-radius: 10px; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 VLTS GATLING NITRO - V89")
st.caption("Enterprise Edition - Optimized Sync")

# --- Initialize States ---
if 'firing' not in st.session_state:
    st.session_state.firing = False
if 'total_count' not in st.session_state:
    st.session_state.total_count = 0
if 'last_portal_update' not in st.session_state:
    st.session_state.last_portal_update = "IDLE"

# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ Configuration")
    tag = st.text_input("TAG", "EGAS")
    imei = st.text_input("IMEI", "862567075041793")
    vno = st.text_input("VEHICLE NO", "BR04GA5974")
    lat = st.text_input("LATITUDE", "25.6501550")
    lon = st.text_input("LONGITUDE", "84.7851780")
    st.divider()
    mode = st.radio("PROTOCOL", ["UDP", "TCP"], horizontal=True)

# --- UI Controls ---
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
m1_placeholder = st.empty()
m2_placeholder = st.empty()

# --- Firing & Scraper Function ---
def get_chrome_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    paths = ["/usr/bin/chromium", "/usr/bin/chromium-browser", "/usr/bin/google-chrome"]
    for path in paths:
        if os.path.exists(path):
            options.binary_location = path
            break
    return webdriver.Chrome(options=options)

# --- Direct Execution Loop ---
if st.session_state.firing:
    target = ("vlts.bihar.gov.in", 9999)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM if mode == "UDP" else socket.SOCK_STREAM)
    
    try:
        if mode == "TCP":
            sock.settimeout(3)
            sock.connect(target)
        
        check_counter = 0
        while st.session_state.firing:
            # 1. Fire Packets (Batch of 100 for higher speed)
            now = datetime.now()
            d, t = now.strftime("%d%m%Y"), now.strftime("%H%M%S")
            packet = f"$PVT,{tag},2.1.1,NR,01,L,{imei},{vno},1,{d},{t},{lat},N,{lon},E,0.00,0.0,11,73,0.8,0.8,airtel,1,1,11.5,4.3,0,C,26,404,73,0a83,e3c8,e3c7,0a83,7,e3fb,0a83,7,c79d,0a83,10,e3f9,0a83,0,0001,00,000041,DDE3*".encode('ascii')
            
            for _ in range(100):
                sock.sendto(packet, target) if mode == "UDP" else sock.send(packet)
            
            st.session_state.total_count += 100
            check_counter += 100
            
            # 2. Update UI Metrics
            with m1_placeholder.container():
                st.metric("Total Packets Sent", f"{st.session_state.total_count:,}")
            with m2_placeholder.container():
                st.metric("Latest Portal Update", st.session_state.last_portal_update)
            
            # 3. Scraper Logic (Every 1000 packets)
            if check_counter >= 1000:
                try:
                    driver = get_chrome_driver()
                    driver.get("https://khanansoft.bihar.gov.in/portal/ePass/ViewPassDetailsNew.aspx")
                    time.sleep(1)
                    driver.execute_script(f"document.getElementsByName('txtVehicleNo')[0].value = '{vno}';")
                    driver.execute_script("__doPostBack('btnSearch','');")
                    time.sleep(1)
                    res = driver.execute_script("var td = document.evaluate(\"//td[contains(text(), 'Challan Date')]\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue; return td ? td.nextElementSibling.nextElementSibling.innerText.trim() : null;")
                    if res:
                        st.session_state.last_portal_update = res
                        if datetime.now().strftime("%d-%b-%Y").upper() in res.upper():
                            st.session_state.firing = False
                    driver.quit()
                except:
                    pass
                check_counter = 0 # Reset check counter
            
            time.sleep(0.05) # Small gap for UI stability
            
    except Exception as e:
        st.error(f"Engine Error: {e}")
    finally:
        sock.close()
        if st.session_state.firing: st.rerun() # Keep loop alive
else:
    m1_placeholder.metric("Total Packets Sent", f"{st.session_state.total_count:,}")
    m2_placeholder.metric("Latest Portal Update", st.session_state.last_portal_update)
