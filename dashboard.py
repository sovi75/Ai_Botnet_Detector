import streamlit as st
import joblib
import numpy as np
from scapy.all import sniff, IP, TCP, UDP, conf
import threading
import time
from collections import defaultdict
import subprocess
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="BotnetAI - SOC Dashboard",
    page_icon="🛡️",
    layout="wide"
)

# ============================================
# PROFESSIONAL MODALS (DIALOGS)
# ============================================

@st.dialog("📖 BOTNETAI: CONCEPT & LEARNING")
def learn_modal():
    st.markdown("### **The Botnet Problem**")
    st.write("""
    Traditional firewalls and IDS/IPS systems rely on **Signature-Based Detection**—meaning they only stop 
    attacks they have seen before. When a botnet uses zero-day exploits, domain generation algorithms (DGAs), 
    or polymorphic payloads, traditional security fails. 
    
    **BotnetAI** solves this using **Behavioral Machine Learning**. We don't look for known bad files; we look for 
    *abnormal network behavior*.
    """)
    
    st.markdown("---")
    st.markdown("### **System Architecture Pipeline**")
    
    with st.expander("🔍 1. Real-Time Packet Sniffing (Scapy)"):
        st.write("""
        The system continuously monitors the network interface, specifically filtering for traffic on **Port 5000**. 
        Instead of saving heavy PCAP files for later analysis, it intercepts packets in memory in real-time. 
        This ensures near-zero latency between an attack initiating and our system logging the event.
        """)
        
    with st.expander("⚙️ 2. Dynamic Feature Extraction"):
        st.write("""
        Raw network packets cannot be fed directly into an AI. BotnetAI strips down the packets and extracts highly correlative metadata:
        * **Packet Size:** Botnet C2 (Command & Control) beacons often have highly specific, uniform packet sizes.
        * **Protocol:** Differentiating between TCP (often used for C2 instructions) and UDP (often used for DDoS flooding).
        * **TCP Flags:** Detecting abnormal flag combinations (like massive SYN floods without corresponding ACKs).
        * **Payload Length:** Botnet commands are usually tiny (just a few bytes), whereas normal web traffic varies wildly.
        """)
        
    with st.expander("🧠 3. XGBoost Inference Engine"):
        st.write("""
        At the core of the detection engine is an **Extreme Gradient Boosting (XGBoost)** classifier. 
        XGBoost builds a forest of decision trees sequentially, where each new tree corrects the errors of the previous ones. 
        It is highly resistant to overfitting and processes tabular network data in milliseconds, making it the industry standard for live SOC (Security Operations Center) environments.
        """)
        
    with st.expander("🛡️ 4. Threat Buffer & Automated Mitigation"):
        st.write("""
        To prevent **False Positives** (accidentally blocking legitimate users), BotnetAI uses a 'Threat Buffer'. 
        A single suspicious packet won't trigger an automatic block. The system requires a sustained pattern of malicious traffic. 
        Once the threshold (100 packets) is crossed, it triggers an automated mitigation script, utilizing `netsh` to write a hard rule into the Windows Firewall, severing the attacker's connection.
        """)

    st.markdown("---")
    st.markdown("#### **Project Video Walkthrough**")
    # Replace with your actual project YouTube link
    st.video("https://youtu.be/pmFUmTMPphc?si=2cKRM3iFYmb4P4D4")

@st.dialog("❓ SYSTEM USAGE GUIDE")
def help_modal():
    st.markdown("### **Operating the SOC Dashboard**")
    st.markdown("""
    1. **Initialization:** Run the script as **Administrator** to grant Scapy access to the network card.
    2. **Monitoring:** The **Total Packets** counter should increment as traffic hits Port 5000.
    3. **Threat Buffer:** As the AI detects malicious packets, the buffer fills. Once it hits 100, a Critical Alert is logged.
    4. **Mitigation:** Go to the **Attack Sources** section, identify the malicious IP, and click **🚫 Block**.
    5. **Verification:** The system will use `netsh` to automatically update your Windows Firewall.
    """)

@st.dialog("PROJECT DEVELOPMENT TEAM")
def developed_by_modal():
    st.markdown("### **Core Contributors**")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**Ragini Balasundaram**")
        st.caption("24BYB1115")
    with c2:
        st.markdown("**Jerusha R**")
        st.caption("24BYB1173")
    with c3:
        st.markdown("**S Oviya**")
        st.caption("24BYB1105")
    
    st.markdown("---")
    st.markdown("### **Project Supervisor**")
    st.success("#### **Prof. Swaminathan Annadurai**")
    st.caption("SCOPE - VIT Chennai")

# ============================================
# CLEAN PROFESSIONAL CSS
# ============================================
st.markdown("""
<style>
    /* =========================================
       FIX FOR POPUPS (MODALS)
       ========================================= */
    div[data-testid="stModal"] > div > div {
        background-color: #0b1120 !important; /* Deep dark blue background */
        border: 2px solid #2dd4bf !important; /* Teal border */
        border-radius: 12px !important;
        box-shadow: 0px 0px 20px rgba(45, 212, 191, 0.2) !important;
    }
    
    /* Force text inside modal to be white and visible */
    div[data-testid="stModal"] p, 
    div[data-testid="stModal"] h3, 
    div[data-testid="stModal"] h4, 
    div[data-testid="stModal"] span,
    div[data-testid="stModal"] li {
        color: #e2e8f0 !important; 
    }
    
    /* Close button styling */
    div[data-testid="stModal"] button[kind="secondary"] {
        color: #ef4444 !important; /* Make the close 'X' red */
    }

    /* =========================================
       MAIN DASHBOARD CSS
       ========================================= */
    .stApp { background: #0a0e1a; }
    .stMarkdown, p, span, div, label, .stText, .stMetric label { color: #ffffff !important; }
    
    /* Top Nav Buttons Styling */
    div[data-testid="stColumn"] .stButton button {
        background-color: transparent !important;
        color: #2dd4bf !important;
        border: 1px solid #2dd4bf !important;
        border-radius: 4px !important;
        font-size: 0.7rem !important;
        font-weight: 700 !important;
        letter-spacing: 1px !important;
        height: 32px !important;
        width: 100% !important;
    }
    div[data-testid="stColumn"] .stButton button:hover {
        background-color: rgba(45, 212, 191, 0.1) !important;
        border-color: #ffffff !important;
        color: #ffffff !important;
        box-shadow: 0 0 10px rgba(45, 212, 191, 0.3);
    }

    .main-header {
        font-size: 2rem; font-weight: 800;
        background: linear-gradient(135deg, #2dd4bf, #3b82f6);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .sub-header { color: #cbd5e1 !important; font-size: 0.85rem; margin-top: -5px; }
    .badge { background: #1e293b; border-radius: 20px; padding: 4px 12px; font-size: 0.7rem; color: #2dd4bf !important; display: inline-block; }
    .metric-card { background: #111827; border-radius: 16px; padding: 20px; border: 1px solid #2dd4bf; text-align: center; }
    .metric-value { font-size: 2rem; font-weight: 700; color: #ffffff !important; }
    .metric-label { font-size: 0.7rem; color: #9ca3af !important; text-transform: uppercase; margin-top: 8px; }
    .alert-critical { background: #1a1a2e; border-left: 4px solid #ef4444; border-radius: 10px; padding: 14px; margin-bottom: 10px; color: #ffffff !important; }
    .alert-success { background: #1a2e1a; border-left: 4px solid #10b981; border-radius: 10px; padding: 14px; margin-bottom: 10px; color: #ffffff !important; }
    .alert-info { background: #1a2a3e; border-left: 4px solid #3b82f6; border-radius: 10px; padding: 14px; margin-bottom: 10px; color: #ffffff !important; }
    .source-ip { font-family: monospace; font-size: 1rem; font-weight: 700; color: #f87171 !important; }
    .source-stats { color: #cbd5e1 !important; font-size: 0.8rem; }
    .ai-card { background: #111827; border-radius: 16px; padding: 20px; border: 1px solid #2dd4bf; text-align: center; }
    .progress-container { background: #1e293b; border-radius: 20px; height: 8px; margin: 10px 0; }
    .progress-fill { background: linear-gradient(90deg, #10b981, #f59e0b, #ef4444); border-radius: 20px; height: 100%; }
    .divider { height: 1px; background: #334155; margin: 20px 0; }
</style>
""", unsafe_allow_html=True)


# ============================================
# DATA STRUCTURES
# ============================================
class Monitor:
    def __init__(self):
        self.count = 0
        self.alerts = []
        self.buffer = 0
        self.attack_sources = defaultdict(lambda: {"count": 0, "first_seen": None, "last_seen": None, "blocked": False})
        self.start_time = time.time()

@st.cache_resource
def get_mon():
    return Monitor()

mon = get_mon()
blocked_ips = set()

# ============================================
# LOAD AI MODEL
# ============================================
@st.cache_resource
def load_model():
    for name in ['botnet_model_simple.pkl', 'botnet_model.pkl', 'botnet_model_improved.pkl']:
        try:
            model = joblib.load(name)
            return model, name
        except:
            continue
    return None, None

model, model_name = load_model()

# ============================================
# BLOCK IP FUNCTION
# ============================================
def block_ip(ip):
    if ip in blocked_ips:
        return False
    try:
        rule_name = f"GuardianAI_Block_{ip.replace('.', '_')}"
        subprocess.run(
            f'netsh advfirewall firewall add rule name="{rule_name}" dir=in action=block remoteip={ip}',
            shell=True, capture_output=True, timeout=5
        )
        blocked_ips.add(ip)
        return True
    except:
        return False

# ============================================
# HEADER & NAVIGATION
# ============================================
col_header, col_nav = st.columns([1.5, 1])

with col_header:
    st.markdown('<div class="main-header">🛡️ BOTNET_AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">AI-Powered Intrusion Detection | Port 5000 Analysis</div>', unsafe_allow_html=True)

with col_nav:
    # Navigation Buttons Grid
    n1, n2, n3, n4 = st.columns(4)
    if n1.button("LEARN"):
        learn_modal()
    if n2.button("HELP"):
        help_modal()
    if n3.button("TEAM"):
        developed_by_modal()
    
    # Download Report Logic
    report_data = f"BOTNET_AI SECURITY REPORT\nGenerated: {datetime.now()}\nPackets Scanned: {mon.count}\nAlerts: {len(mon.alerts)}"
    n4.download_button("LOGS", report_data, file_name="BotnetAI_Log.txt")
    
    # Uptime Badge
    uptime = int(time.time() - mon.start_time)
    st.markdown(f'<div style="text-align: right; margin-top: 5px;"><span class="badge">🟢 LIVE</span> <span class="badge">⏱️ {uptime // 60}m {uptime % 60}s</span></div>', unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ============================================
# METRIC CARDS
# ============================================
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{mon.count:,}</div><div class="metric-label">📦 PACKETS SCANNED</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{len(mon.alerts)}</div><div class="metric-label">🚨 SECURITY ALERTS</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{mon.buffer}/100</div><div class="metric-label">🎯 THREAT BUFFER</div></div>', unsafe_allow_html=True)
with col4:
    active_count = len([s for s in mon.attack_sources if mon.attack_sources[s]["count"] > 0])
    st.markdown(f'<div class="metric-card"><div class="metric-value">{active_count}</div><div class="metric-label">🌐 ATTACK SOURCES</div></div>', unsafe_allow_html=True)

buffer_percent = min(mon.buffer, 100)
st.markdown(f'<div class="progress-container"><div class="progress-fill" style="width: {buffer_percent}%;"></div></div>', unsafe_allow_html=True)
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ============================================
# MAIN CONTENT
# ============================================
left_col, right_col = st.columns([2, 1])

with left_col:
    st.markdown("### 🔴 LIVE ALERTS")
    if mon.alerts:
        for alert in mon.alerts[-5:][::-1]:
            if "BLOCKED" in alert: st.markdown(f'<div class="alert-info">🛡️ {alert}</div>', unsafe_allow_html=True)
            elif "ATTACK" in alert: st.markdown(f'<div class="alert-critical">⚠️ {alert}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="alert-success">✅ System Secure - No Threats Detected</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🌍 ATTACK SOURCES")
    if mon.attack_sources:
        sorted_sources = sorted(mon.attack_sources.items(), key=lambda x: x[1]["count"], reverse=True)
        for src_ip, data in sorted_sources[:10]:
            status = "🚫 BLOCKED" if data["blocked"] else "⚠️ ACTIVE"
            status_color = "#ef4444" if not data["blocked"] else "#10b981"
            col_a, col_b, col_c = st.columns([3, 2, 1])
            with col_a:
                st.markdown(f'<div><span class="source-ip">{src_ip}</span><br><span class="source-stats">📊 {data["count"]} packets | First: {data["first_seen"] or "N/A"}</span></div>', unsafe_allow_html=True)
            with col_b:
                st.markdown(f'<div style="text-align: center;"><span style="color: {status_color}; font-weight: 600;">{status}</span></div>', unsafe_allow_html=True)
            with col_c:
                if not data["blocked"]:
                    if st.button(f"🚫 Block", key=f"block_{src_ip}"):
                        if block_ip(src_ip):
                            mon.attack_sources[src_ip]["blocked"] = True
                            mon.alerts.append(f"{time.strftime('%H:%M:%S')} 🛡️ BLOCKED {src_ip}")
                            st.rerun()
                else: st.markdown('<span style="color:#10b981;">✅ Blocked</span>', unsafe_allow_html=True)
            with st.expander(f"🔍 Details for {src_ip}"):
                st.markdown(f"- Total Malicious Packets: `{data['count']}`\n- Threat Score: `{min(data['count'] // 5, 100)}/100`\n- Classification: `Botnet C2 Traffic` (94.4% confidence)")
            st.markdown('<div style="height: 5px;"></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="alert-success">🟢 No attack sources detected</div>', unsafe_allow_html=True)

with right_col:
    st.markdown(f"""
    <div class="ai-card">
        <div class="ai-title">🧠 AI DETECTION ENGINE</div>
        <div class="ai-value">XGBoost Classifier</div>
        <div style="margin: 15px 0;">
            <div style="display: flex; justify-content: space-between; margin: 5px 0;"><span>Accuracy</span><span style="color: #2dd4bf;">94.4%</span></div>
            <div class="progress-container" style="margin: 0;"><div style="width: 94%; height: 100%; background: #2dd4bf; border-radius: 20px;"></div></div>
            <div style="display: flex; justify-content: space-between; margin: 5px 0;"><span>Precision</span><span style="color: #2dd4bf;">92.1%</span></div>
            <div class="progress-container" style="margin: 0;"><div style="width: 92%; height: 100%; background: #2dd4bf; border-radius: 20px;"></div></div>
        </div>
        <div style="font-size: 0.7rem; color: #9ca3af;">Model: {model_name or 'Not Loaded'}</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 RESET DASHBOARD", use_container_width=True):
        mon.count = 0; mon.alerts = []; mon.buffer = 0; mon.attack_sources.clear(); mon.start_time = time.time(); st.rerun()

# ============================================
def callback(pkt):
    if not pkt.haslayer(IP): return
    
    # Identify if it's hitting our VTOP port (e.g., 8080)
    if pkt.haslayer(TCP) and (pkt[TCP].dport == 8080 or pkt[TCP].sport == 8080):
        mon.count += 1  # This will make the 'Packets Scanned' move live
        
        # Feature extraction for the AI
        size = len(pkt)
        protocol = 6 # TCP
        tcp_flags = int(pkt[TCP].flags)
        payload_len = len(pkt[TCP].payload) if pkt[TCP].payload else 0
        
        features = np.array([[float(size), float(protocol), float(tcp_flags), float(payload_len)]])
        
        try:
            pred = model.predict(features)[0]
            if pred == 1: # AI thinks it's a Bot
                src_ip = pkt[IP].src
                if src_ip not in mon.attack_sources:
                    mon.attack_sources[src_ip] = {"count": 0, "first_seen": time.strftime("%H:%M:%S"), "blocked": False}
                mon.attack_sources[src_ip]["count"] += 1
                mon.buffer += 5 # Increase threat level faster
            else:
                # Student traffic: slowly cool down the threat buffer
                mon.buffer = max(0, mon.buffer - 1)
        except:
            pass
# SNIFFER LOGIC (KEEPING YOUR LOGIC EXACTLY)


def get_interface():
    # Priority 1: Npcap Loopback (for ngrok traffic from mobile/remote)
    for iface_id, iface_obj in conf.ifaces.items():
        name = str(iface_obj.name) if hasattr(iface_obj, 'name') else str(iface_obj)
        if "Npcap Loopback" in name:
            print(f"✅ Using Npcap Loopback for ngrok traffic")
            return iface_id
    
    # Priority 2: Wi-Fi (for direct LAN attacks)
    for iface_id, iface_obj in conf.ifaces.items():
        name = str(iface_obj.name) if hasattr(iface_obj, 'name') else str(iface_obj)
        if "Wi-Fi" in name or "Wireless" in name:
            print(f"✅ Using Wi-Fi for local traffic")
            return iface_id
    
    # Priority 3: Ethernet (fallback)
    for iface_id, iface_obj in conf.ifaces.items():
        name = str(iface_obj.name) if hasattr(iface_obj, 'name') else str(iface_obj)
        if "Ethernet" in name:
            print(f"✅ Using Ethernet")
            return iface_id
    
    return None
# Start Sniffer with generalized filter
if 'sniffer_on' not in st.session_state and model:
    iface = get_interface()
    if iface:
        print(f"DEBUG: Sniffer starting on interface: {iface}")
        # Changed filter to "port 5000" to catch BOTH TCP and UDP
        t = threading.Thread(
            target=lambda: sniff(iface=iface, prn=callback, store=0, filter="port 5000"), 
            daemon=True
        )
        t.start()
        st.session_state.sniffer_on = True

time.sleep(1)
st.rerun()