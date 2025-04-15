import socket
import sys
import struct
import binascii
import time
import subprocess

def mac_bytes_to_str(mac_bytes):
    return ':'.join(f'{b:02x}' for b in mac_bytes)

def mac_str_to_bytes(mac):
    return binascii.unhexlify(mac.replace(':', '').replace('-', ''))

def get_interface_mac(interface):
    """獲取網絡介面的 MAC 地址"""
    try:
        with open(f'/sys/class/net/{interface}/address', 'r') as f:
            return f.read().strip()
    except:
        return None

def set_promiscuous_mode(interface, enable=True):
    """設置網路介面的混雜模式"""
    try:
        mode = "promisc" if enable else "-promisc"
        subprocess.run(['ip', 'link', 'set', interface, mode], check=True)
        return True
    except Exception as e:
        print(f"設置混雜模式失敗: {e}")
        return False

def main():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print(f"用法: sudo python {sys.argv[0]} <interface> [sender_mac]")
        sys.exit(1)
        
    interface = sys.argv[1]
    
    # 自動檢測接口的 MAC
    detected_mac = get_interface_mac(interface)
    if detected_mac:
        print(f"檢測到介面 {interface} 的 MAC 地址: {detected_mac}")
        use_detected = input("是否使用此 MAC 地址? (y/n): ").lower() == 'y'
        if use_detected:
            my_mac = detected_mac
        else:
            my_mac = "94:c6:91:a9:5d:26"
    else:
        my_mac = "94:c6:91:a9:5d:26"
    
    # 廣播地址選項
    listen_broadcast = input("是否監聽廣播封包? (y/n): ").lower() == 'y'
    
    # 混雜模式選項
    use_promisc = input("是否啟用混雜模式? (y/n): ").lower() == 'y'
    if use_promisc:
        if set_promiscuous_mode(interface):
            print(f"已將 {interface} 設置為混雜模式")
    
    # 如果提供了發送者MAC，則使用；否則使用默認發送者MAC
    if len(sys.argv) == 3:
        sender_mac = sys.argv[2]
        filter_sender = input("是否只接收來自此MAC的封包? (y/n): ").lower() == 'y'
    else:
        sender_mac = "00:15:5d:3f:70:f7"  # 發送者的 MAC 地址
        filter_sender = False
        
    sender_mac_bytes = mac_str_to_bytes(sender_mac)
    my_mac_bytes = mac_str_to_bytes(my_mac)
    
    # 嘗試使用特定的 EtherType 過濾
    try:
        # 首先嘗試過濾特定的 EtherType
        s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x88B5))
        print("使用特定 EtherType 過濾 (0x88B5)")
    except Exception as e:
        print(f"無法使用特定EtherType過濾: {e}")
        # 如果失敗，捕獲所有類型的以太網幀
        s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
        print("捕獲所有類型的以太網幀")
    
    try:
        s.bind((interface, 0))
        print(f"成功綁定到接口 {interface}")
    except Exception as e:
        print(f"接口綁定失敗: {e}")
        sys.exit(1)
    
    print(f"監聽 {interface} 上發往 MAC {my_mac} 的封包")
    if listen_broadcast:
        print("同時監聽發往廣播地址的封包")
    if filter_sender:
        print(f"只接收來自 MAC {sender_mac} 的封包")
    else:
        print(f"接收來自任何MAC地址的封包")
    print("等待封包中...")
    
    packet_count = 0
    start_time = time.time()
    while True:
        # 設置超時機制，避免無限等待
        current_time = time.time()
        if current_time - start_time > 60:  # 60秒超時
            print(f"已等待60秒，共接收到 {packet_count} 個封包")
            if packet_count == 0:
                print("未接收到封包，請檢查網路連接與配置")
            break
            
        try:
            frame = s.recv(1600)
        except socket.timeout:
            continue
        except Exception as e:
            print(f"接收封包時發生錯誤: {e}")
            continue
            
        if len(frame) < 14:
            continue  # 忽略過小的幀
            
        # 解析以太網幀
        dst_mac = frame[0:6]
        src_mac = frame[6:12]
        ether_type = struct.unpack('!H', frame[12:14])[0]
        
        # 更詳細的封包信息 (調試模式)
        if not packet_count and (current_time - start_time) > 10:
            print(f"\n接收到封包 (調試模式):")
            print(f"來源 MAC: {mac_bytes_to_str(src_mac)} -> 目的 MAC: {mac_bytes_to_str(dst_mac)}")
            print(f"EtherType: 0x{ether_type:04X}")
            print(f"是否匹配目標MAC: {dst_mac == my_mac_bytes}")
            print(f"是否為廣播: {dst_mac == b'\xff\xff\xff\xff\xff\xff'}")
            if filter_sender:
                print(f"是否匹配發送MAC: {src_mac == sender_mac_bytes}")
            
        # 針對目標MAC過濾 (必須檢查) - 也接受廣播地址
        broadcast_mac = b"\xff\xff\xff\xff\xff\xff"
        if dst_mac != my_mac_bytes and (not listen_broadcast or dst_mac != broadcast_mac):
            continue
            
        # 如果需要過濾發送者，則檢查發送者MAC
        if filter_sender and src_mac != sender_mac_bytes:
            continue
            
        # 如果是我們想要的封包
        packet_count += 1
        payload = frame[14:]
        print("\n收到符合條件的封包:")
        print(f"來源 MAC: {mac_bytes_to_str(src_mac)} -> 目的 MAC: {mac_bytes_to_str(dst_mac)}")
        print(f"EtherType: 0x{ether_type:04X}")
        print(f"Payload: {payload.decode(errors='ignore')}")
        if dst_mac == broadcast_mac:
            print("(這是一個廣播封包)")
        print("-" * 50)
        start_time = time.time()  # 重置計時器

if __name__ == '__main__':
    main()
