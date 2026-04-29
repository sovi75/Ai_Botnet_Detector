from scapy.all import sniff, IP, TCP, conf
import time

# Your Wi-Fi interface ID from earlier
WIFI_IFACE = r"\Device\NPF_{45A5D929-A2E7-4B65-9536-D784073213B2}"

def packet_handler(pkt):
    if pkt.haslayer(IP) and pkt.haslayer(TCP):
        if pkt[TCP].dport == 5000 or pkt[TCP].sport == 5000:
            print(f"✅ CAPTURED: {pkt[IP].src}:{pkt[TCP].sport} -> {pkt[IP].dst}:{pkt[TCP].dport} size={len(pkt)}")

print("=" * 50)
print("Testing Wi-Fi sniffer on port 5000")
print("Interface:", WIFI_IFACE)
print("=" * 50)
print("Now run from Ubuntu: ab -n 100 -c 10 http://192.168.191.58:5000/")
print("Waiting 30 seconds for packets...\n")

sniff(iface=WIFI_IFACE, prn=packet_handler, store=0, filter="tcp port 5000", timeout=30)

print("\nTest complete.")