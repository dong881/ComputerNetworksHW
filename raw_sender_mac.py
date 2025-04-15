import socket
import sys
import binascii
import struct
import time

def mac_str_to_bytes(mac):
    return binascii.unhexlify(mac.replace(':', ''))

def main():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print(f"用法: sudo python {sys.argv[0]} <interface> [dst_mac]")
        sys.exit(1)
        
    interface = sys.argv[1]
    # 如果指定了目標MAC，則使用；否則使用默認的接收者MAC
    if len(sys.argv) == 3:
        dst_mac = sys.argv[2]
    else:
        dst_mac = "18:31:bf:93:7a:80"  # 更新為接收者的 MAC
    
    # 也可以使用廣播地址嘗試
    # dst_mac = "ff:ff:ff:ff:ff:ff"
    
    ether_type = 0x88B5  # 自訂 EtherType
    
    # 構建以太網幀
    dst_mac_bytes = mac_str_to_bytes(dst_mac)
    src_mac_bytes = b'\x00\x00\x00\x00\x00\x00'  # 系統會自動填充
    
    # 創建並發送
    s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
    s.bind((interface, 0))
    
    # 發送多個封包，增加接收機會
    for i in range(5):
        payload = f"Hello Layer2 Only! Packet #{i+1}".encode()
        frame = dst_mac_bytes + src_mac_bytes + struct.pack('!H', ether_type) + payload
        s.send(frame)
        print(f"發送第 {i+1} 個封包...")
        time.sleep(1)  # 間隔發送，防止封包丟失
    
    # 取得實際發送的 MAC 地址
    src_mac_actual = ':'.join(f'{b:02x}' for b in bytes.fromhex(s.getsockname()[4].hex()))
    print(f"已送出Layer2乙太網路幀")
    print(f"發送者 MAC: {src_mac_actual}")
    print(f"接收者 MAC: {dst_mac}")
    print(f"EtherType: 0x{ether_type:04X}")
    print(f"提示: 請確保發送和接收的機器位於同一網段，且使用相同的EtherType")
    s.close()

if __name__ == '__main__':
    main()