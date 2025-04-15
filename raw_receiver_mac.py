import socket
import sys
import struct
import binascii
import time

def mac_bytes_to_str(mac_bytes):
    return ':'.join(f'{b:02x}' for b in mac_bytes)

def mac_str_to_bytes(mac):
    return binascii.unhexlify(mac.replace(':', '').replace('-', ''))

def main():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print(f"用法: sudo python {sys.argv[0]} <interface> [sender_mac]")
        sys.exit(1)
        
    interface = sys.argv[1]
    
    # 更新為接收者實際的 MAC 地址
    my_mac = "94:c6:91:a9:5d:26"  # 接收者的實際 MAC 地址
    
    # 如果提供了發送者MAC，則使用；否則使用默認發送者MAC
    if len(sys.argv) == 3:
        sender_mac = sys.argv[2]
    else:
        sender_mac = "00:15:5d:3f:70:f7"  # 發送者的 MAC 地址
        
    sender_mac_bytes = mac_str_to_bytes(sender_mac)
    filter_sender = True
    
    my_mac_bytes = mac_str_to_bytes(my_mac)
    
    # 嘗試使用特定的 EtherType 過濾
    try:
        # 首先嘗試過濾特定的 EtherType
        s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x88B5))
        print("使用特定 EtherType 過濾 (0x88B5)")
    except:
        # 如果失敗，捕獲所有類型的以太網幀
        s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
        print("捕獲所有類型的以太網幀")
    
    s.bind((interface, 0))
    
    print(f"監聽 {interface} 上來自 MAC {sender_mac} 發往 MAC {my_mac} 的封包")
    print("等待封包中...")
    
    start_time = time.time()
    while True:
        # 設置超時機制，避免無限等待
        if time.time() - start_time > 60:  # 60秒超時
            print("已等待60秒，未接收到封包，請檢查網路連接與配置")
            break
            
        frame = s.recv(1600)
        if len(frame) < 14:
            continue  # 忽略過小的幀
            
        # 解析以太網幀
        dst_mac = frame[0:6]
        src_mac = frame[6:12]
        ether_type = struct.unpack('!H', frame[12:14])[0]
        
        # 針對目標MAC過濾 (必須檢查)
        if dst_mac != my_mac_bytes:
            continue
            
        # 如果需要過濾發送者，則檢查發送者MAC
        if filter_sender and src_mac != sender_mac_bytes:
            continue
            
        # 如果是我們想要的封包
        payload = frame[14:]
        print("\n收到符合條件的封包:")
        print(f"來源 MAC: {mac_bytes_to_str(src_mac)} -> 目的 MAC: {mac_bytes_to_str(dst_mac)}")
        print(f"EtherType: 0x{ether_type:04X}")
        print(f"Payload: {payload.decode(errors='ignore')}")
        print("-" * 50)
        start_time = time.time()  # 重置計時器

if __name__ == '__main__':
    main()
