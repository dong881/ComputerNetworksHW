import socket
import sys
import struct
import binascii

def mac_bytes_to_str(mac_bytes):
    return ':'.join(f'{b:02x}' for b in mac_bytes)

def main():
    if len(sys.argv) != 2:
        print(f"用法: sudo python {sys.argv[0]} <interface>")
        sys.exit(1)
        
    interface = sys.argv[1]
    my_mac = "94:c6:91:a9:5d:26"  # 接收者的 MAC
    my_mac_bytes = binascii.unhexlify(my_mac.replace(':', ''))
    
    # 使用 0x0003 (ETH_P_ALL) 捕獲所有類型的以太網幀
    s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
    s.bind((interface, 0))
    
    print(f"監聽 {interface} 上發往 MAC {my_mac} 的封包")
    
    while True:
        frame = s.recv(1600)
        if len(frame) < 14:
            continue  # 忽略過小的幀
            
        # 解析以太網幀
        dst_mac = frame[0:6]
        src_mac = frame[6:12]
        ether_type = struct.unpack('!H', frame[12:14])[0]
        payload = frame[14:]
        
        # 只處理發往目標 MAC 的封包 (我們的接收器 MAC)
        if dst_mac == my_mac_bytes:
            print(f"收到封包:")
            print(f"來源 MAC: {mac_bytes_to_str(src_mac)}")
            print(f"目的 MAC: {mac_bytes_to_str(dst_mac)}")
            print(f"EtherType: 0x{ether_type:04X}")
            print(f"Payload: {payload.decode(errors='ignore')}")
            print("-" * 50)

if __name__ == '__main__':
    main()
