import socket
import sys
import binascii
import struct

def mac_str_to_bytes(mac):
    return binascii.unhexlify(mac.replace(':', ''))

def main():
    if len(sys.argv) != 2:
        print(f"用法: sudo python {sys.argv[0]} <interface>")
        sys.exit(1)
        
    interface = sys.argv[1]
    # 接收者的 MAC
    dst_mac = "94:c6:91:a9:5d:26"
    ether_type = 0x88B5  # 自訂 EtherType
    payload = b'Hello Layer2 Only!'
    
    # 構建以太網幀
    dst_mac_bytes = mac_str_to_bytes(dst_mac)
    # 發送者的 MAC - 會由系統自動填充
    src_mac_bytes = b'\x00\x00\x00\x00\x00\x00'
    
    frame = dst_mac_bytes + src_mac_bytes + struct.pack('!H', ether_type) + payload
    
    # 創建並發送
    s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
    s.bind((interface, 0))
    s.send(frame)
    
    # 取得實際發送的 MAC 地址
    src_mac_actual = ':'.join(f'{b:02x}' for b in bytes.fromhex(s.getsockname()[4].hex()))
    print(f"已送出Layer2乙太網路幀")
    print(f"發送者 MAC: {src_mac_actual}")
    print(f"接收者 MAC: {dst_mac}")
    print(f"EtherType: 0x{ether_type:04X}")
    s.close()

if __name__ == '__main__':
    main()