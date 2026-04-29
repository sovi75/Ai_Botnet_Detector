from scapy.all import sniff, IP, TCP, UDP, conf
import time

def simple_callback(pkt):
    if pkt.haslayer(IP):
        src = pkt[IP].src
        dst = pkt[IP].dst
        proto = "TCP" if pkt.haslayer(TCP) else "UDP" if pkt.haslayer(UDP) else "Other"
        size = len(pkt)
        sport = pkt[TCP].sport if pkt.haslayer(TCP) else pkt[UDP].sport if pkt.haslayer(UDP) else 0
        dport = pkt[TCP].dport if pkt.haslayer(TCP) else pkt[UDP].dport if pkt.haslayer(UDP) else 0
        print(f"[CAPTURED] {src}:{sport} -> {dst}:{dport} | {proto} | Size: {size}")

# SPECIFIC INTERFACE IDs FROM YOUR SYSTEM
interfaces_to_test = {
    "Npcap Loopback": r"\Device\NPF_{4E480765-90F7-449B-A570-4415B1A4BFEC}",
    "Wi-Fi": r"\Device\NPF_{45A5D929-A2E7-4B65-9536-D784073213B2}",
    "Ethernet": r"\Device\NPF_{BB71FC93-6087-4D2B-B52C-E9E195D7DD95}",
}

print("=" * 60)
print("Testing each interface for 10 seconds...")
print("Open your VTOP ngrok URL in browser during this test")
print("=" * 60)

for name, iface_id in interfaces_to_test.items():
    print(f"\n[TESTING] {name} - {iface_id}")
    print("Listening for 10 seconds...")
    
    try:
        packets = sniff(iface=iface_id, timeout=10, store=0, prn=simple_callback)
        print(f"[RESULT] {name}: Completed")
    except Exception as e:
        print(f"[ERROR] {name}: {str(e)[:100]}")
    
    print("-" * 40)

print("\n[DONE] Which interface showed your VTOP traffic?")