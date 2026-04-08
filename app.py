import streamlit as st
import socket
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os

# --- Page Setup ---
st.set_page_config(page_title="GATLING NITRO V88", page_icon="🚀", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #050505; color: #00FF00; }
    div.stButton > button {
        background-color: #004400; color: white; border-radius: 8px; font-weight: bold; width: 100%; height: 3.5em;
    }
    .stMetric { background-color: #111; padding: 15px; border-radius: 10px; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 VLTS GATLING NITRO - V88")
st.caption("Enterprise Edition - Direct UI Sync")

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

# --- Direct Execution Loop ---
if st.session_state.firing:
    # Setup Socket Once
    target = ("vlts.bihar.gov.in", 9999)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM if mode == "UDP" else socket.SOCK_STREAM)
    if mode == "TCP":
        sock.settimeout(3)
        try: sock.connect(target)
        except: st.error("TCP Connection Failed")
    
    # Start Execution
    while st.session_state.firing:
        # 1. Fire Packets (Batch of 50 for speed)
        now = datetime.now()
        d, t = now.strftime("%d%m%Y"), now.strftime("%H%M%S")
        packet = f"$PVT,{tag},2.1.1,NR,01,L,{imei},{vno},1,{d},{t},{lat},N,{lon},E,0.00,0.0,11,73,0.8,0.8,airtel,1,1,11.5,4.3,0,C,26,404,73,0a83,e3c8,e3c7,0a83,7,e3fb,0a83,7,c79d,0a83,10,e3f9,0a83,0,0001,00,000041,DDE3*".encode('ascii')
        
        for _ in range(50):
            sock.sendto(packet, target) if mode == "UDP" else sock.send(packet)
        
        st.session_state.total_count += 50
        
        # 2. Update UI
        with m1_placeholder.container():
            st.metric("Total Packets Sent", f"{st.session_state.total_count:,}")
        with m2_placeholder.container():
            st.metric("Latest Portal Update", st.session_state.last_portal_update)
        
        # 3. Scraper Logic (Every 500 packets)
        if st.session_state.total_count % 500 == 0:
            # We use a placeholder for status
            st.toast(f"Checking Portal for {vno}...")
            # Note: Headless browser launch here might slow down firing, 
            # so we do it quickly
            # [Optional: Insert Scraper Logic Here if needed]
            
        time.sleep(0.1) # UI stability gap
        
        # Check if Stop button was pressed (Streamlit reruns on interaction)
        # But in a while loop, we need a break condition
        # This is a trick: Streamlit won't show the button press until loop ends
        # So we add a small check
        # if st.button("Emergency Break"): break

    sock.close()
else:
    m1_placeholder.metric("Total Packets Sent", f"{st.session_state.total_count:,}")
    m2_placeholder.metric("Latest Portal Update", st.session_state.last_portal_update)
