import socket
import sys
import binascii
import struct

def mac_str_to_bytes(mac):
    return binascii.unhexlify(mac.replace(':', ''))

def main():
    if len(sys.argv) != 3:
        print(f"用法: sudo python {sys.argv[0]} <interface> <src_mac>")
        sys.exit(1)
    interface = sys.argv[1]
    src_mac = sys.argv[2]
    dst_mac = "94:c6:91:a9:5d:26"  # 預設目標 MAC
    ether_type = 0x88B5  # 自訂 EtherType，避免被上層協定處理
    payload = b'Hello Layer2 Only!'
    frame = mac_str_to_bytes(dst_mac) + mac_str_to_bytes(src_mac) + struct.pack('!H', ether_type) + payload
    s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
    s.bind((interface, 0))
    s.send(frame)
    print(f"已送出Layer2乙太網路幀到 {dst_mac} (src={src_mac}) 於 {interface}")
    s.close()

if __name__ == '__main__':
    main()