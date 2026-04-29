from scapy.all import sniff, IP, TCP, conf
import csv
import time

# Find Npcap Loopback
def get_interface():
    for iface_id, iface_obj in conf.ifaces.items():
        name = str(iface_obj.name) if hasattr(iface_obj, 'name') else str(iface_obj)
        if "Npcap Loopback" in name:
            return iface_id
    return None

# Callback to save packets
packets_data = []

def capture_callback(pkt):
    if not pkt.haslayer(IP) or not pkt.haslayer(TCP):
        return
    
    # Only port 5000
    if pkt[TCP].dport != 5000 and pkt[TCP].sport != 5000:
        return
    
    size = len(pkt)
    protocol = 6
    tcp_flags = int(pkt[TCP].flags)
    payload_len = len(pkt[TCP].payload) if pkt[TCP].payload else 0
    
    packets_data.append([size, protocol, tcp_flags, payload_len])
    print(f"Captured: size={size}, flags={tcp_flags}, payload={payload_len}")

print("=" * 50)
print("Capturing YOUR normal traffic for 60 seconds")
print("During this time, use VTOP normally (login, browse, etc)")
print("=" * 50)

iface = get_interface()
if iface:
    sniff(iface=iface, prn=capture_callback, store=0, filter="tcp port 5000", timeout=60)
    
    # Save to CSV
    import pandas as pd
    df = pd.DataFrame(packets_data, columns=['packet_size', 'protocol', 'tcp_flags', 'payload_len'])
    df.to_csv('my_benign_traffic.csv', index=False)
    print(f"\n✅ Captured {len(packets_data)} benign packets. Saved to 'my_benign_traffic.csv'")
else:
    print("Interface not found")python -c "
from scapy.all import sniff, IP, TCP, conf
import csv
import time

def get_interface():
    for iface_id, iface_obj in conf.ifaces.items():
        name = str(iface_obj.name) if hasattr(iface_obj, 'name') else str(iface_obj)
        if 'Npcap Loopback' in name:
            return iface_id
    return None

packets = []
def cb(pkt):
    if pkt.haslayer(IP) and pkt.haslayer(TCP):
        if pkt[TCP].dport == 5000 or pkt[TCP].sport == 5000:
            size = len(pkt)
            if size not in [44, 54, 66]:
                packets.append([size, 6, int(pkt[TCP].flags), len(pkt[TCP].payload) if pkt[TCP].payload else 0])
                print(f'Captured: {len(packets)} packets', end='\r')

print('Capturing benign traffic for 3 minutes...')
print('Please use VTOP normally (login, browse, refresh many times)')
iface = get_interface()
if iface:
    sniff(iface=iface, prn=cb, store=0, filter='tcp port 5000', timeout=180)
    
    import pandas as pd
    df = pd.DataFrame(packets, columns=['packet_size', 'protocol', 'tcp_flags', 'payload_len'])
    df.to_csv('my_benign_traffic.csv', index=False)
    print(f'\n✅ Captured {len(packets)} benign packets')
else:
    print('Interface not found')
"