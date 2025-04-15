import socket
import binascii
import sys
import struct

def mac_str_to_bytes(mac):
    return binascii.unhexlify(mac.replace(':', ''))

def mac_bytes_to_str(mac_bytes):
    return ':'.join(f'{b:02x}' for b in mac_bytes)

def main():
    if len(sys.argv) != 2:
        print(f"用法: sudo python {sys.argv[0]} <interface>")
        sys.exit(1)
    interface = sys.argv[1]
    target_mac = b'\x00\x15\x5d\x3f\x70\xf7'  # 目標MAC
    s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
    s.bind((interface, 0))
    print(f"僅監聽目標MAC {mac_bytes_to_str(target_mac)} 的乙太網路幀")
    while True:
        frame = s.recv(1600)
        if len(frame) < 14:
            continue  # 不完整的乙太網路幀
        dst_mac = frame[0:6]
        if dst_mac != target_mac:
            continue  # 只處理目標MAC
        src_mac = frame[6:12]
        ether_type = struct.unpack('!H', frame[12:14])[0]
        payload = frame[14:]
        print(f"來源: {mac_bytes_to_str(src_mac)} -> 目的: {mac_bytes_to_str(dst_mac)} | EtherType: 0x{ether_type:04x} | Payload: {payload.decode(errors='ignore')}")

if __name__ == '__main__':
    main()
