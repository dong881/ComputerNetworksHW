import sys
from scapy.all import sniff, Ether, conf

def packet_handler(pkt):
    if pkt.haslayer(Ether) and pkt.type == 0x1234:
        data = bytes(pkt.payload)
        print(f"Src MAC: {pkt.src}, Dst MAC: {pkt.dst}, Data: {data}")

def main():
    iface = "Ethernet"       # Windows 介面名稱
    eth_proto = 0x1234       # 自訂 EtherType
    conf.iface = iface
    print(f"Sniffing on {iface}, filtering EtherType=0x{eth_proto:04X}")
    sniff(iface=iface, prn=packet_handler, store=False)

if __name__ == '__main__':
    main()
