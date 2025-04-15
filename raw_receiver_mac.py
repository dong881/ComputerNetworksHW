import socket
import binascii
import sys

def mac_str_to_bytes(mac):
    return binascii.unhexlify(mac.replace(':', ''))

def main():
    if len(sys.argv) != 2:
        print(f"用法: sudo python {sys.argv[0]} <interface>")
        sys.exit(1)
    interface = sys.argv[1]
    target_mac = b'\x94\xc6\x91\xa9\x5d\x26'  # 目標MAC
    s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
    s.bind((interface, 0))
    print(f"監聽 {interface} 上所有乙太網路幀，僅顯示目標MAC {binascii.hexlify(target_mac, ':').decode()}")
    while True:
        frame = s.recv(1600)
        dst_mac = frame[0:6]
        if dst_mac == target_mac:
            print(f"收到來自 {':'.join(f'{b:02x}' for b in dst_mac)} 的乙太網路幀: {frame[14:].decode(errors='ignore')}")

if __name__ == '__main__':
    main()
