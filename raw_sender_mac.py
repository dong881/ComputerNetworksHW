import socket
import sys
import binascii
import struct
import time
import subprocess

def mac_str_to_bytes(mac):
    return binascii.unhexlify(mac.replace(':', '').replace('-', ''))

def get_interface_mac(interface):
    """獲取網絡介面的 MAC 地址"""
    try:
        with open(f'/sys/class/net/{interface}/address', 'r') as f:
            return f.read().strip()
    except:
        return None

def check_network_route(dst_ip):
    """檢查網路路由，確保目標可達"""
    try:
        result = subprocess.run(['ping', '-c', '1', '-W', '1', dst_ip], 
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0
    except:
        return False

def main():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print(f"用法: sudo python {sys.argv[0]} <interface> [dst_mac]")
        sys.exit(1)
        
    interface = sys.argv[1]
    
    # 獲取發送介面的MAC地址
    src_mac = get_interface_mac(interface)
    if not src_mac:
        print(f"無法獲取介面 {interface} 的MAC地址")
        sys.exit(1)
    print(f"發送介面 {interface} 的MAC地址: {src_mac}")
    
    # 如果指定了目標MAC，則使用；否則使用默認的接收者MAC
    if len(sys.argv) == 3:
        dst_mac = sys.argv[2]
    else:
        dst_mac = "18:31:BF:93:7A:80"  # 更新為接收者的實際 MAC
    
    # 在開始前，檢查網路連通性
    receiver_ip = input("請輸入接收端IP地址 (留空跳過檢查): ")
    if receiver_ip:
        if not check_network_route(receiver_ip):
            print(f"警告: 無法 ping 通接收端 {receiver_ip}")
            print("Layer 2 封包只能在同一個網段內傳送，不能跨越路由器")
            if input("是否仍要嘗試發送? (y/n): ").lower() != 'y':
                sys.exit(1)
    
    # 嘗試使用廣播地址，增加被接收機會
    use_broadcast = False
    if len(sys.argv) < 3 or input("是否嘗試使用廣播地址? (y/n): ").lower() == 'y':
        dst_mac = "ff:ff:ff:ff:ff:ff"
        use_broadcast = True
        print("使用廣播地址發送封包")
    
    ether_type = 0x88B5  # 自訂 EtherType
    
    # 構建以太網幀
    dst_mac_bytes = mac_str_to_bytes(dst_mac)
    src_mac_bytes = mac_str_to_bytes(src_mac)  # 顯式指定源MAC地址
    
    # 創建並發送
    try:
        # 使用正確的socket類型
        s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
        s.bind((interface, 0))
        print(f"成功綁定到接口 {interface}")
    except Exception as e:
        print(f"創建或綁定socket失敗: {e}")
        sys.exit(1)
    
    # 發送多個封包，增加接收機會
    packets_sent = 0
    num_packets = 20  # 增加發送次數
    
    for i in range(num_packets):
        try:
            payload = f"Hello Layer2 Only! Packet #{i+1} from {src_mac} at {time.time()}".encode()
            # 確保封包大小適中
            payload = payload.ljust(100, b' ')  # 確保有一定大小但不超過MTU
            frame = dst_mac_bytes + src_mac_bytes + struct.pack('!H', ether_type) + payload
            bytes_sent = s.send(frame)
            packets_sent += 1
            print(f"發送第 {i+1} 個封包 ({bytes_sent} 字節)...")
            time.sleep(0.2)  # 縮短間隔，更密集發送
        except Exception as e:
            print(f"發送封包時出錯: {e}")
    
    # 取得實際發送的 MAC 地址
    print(f"已送出 {packets_sent}/{num_packets} 個 Layer2 乙太網路幀")
    print(f"發送者 MAC: {src_mac}")
    print(f"接收者 MAC: {dst_mac}")
    print(f"EtherType: 0x{ether_type:04X}")
    if use_broadcast:
        print("廣播封包已發送，任何監聽的機器都可能收到")
    print("\n故障排除提示:")
    print("1. 確保兩台機器直接連接或在同一個交換機上，不能有路由器分隔")
    print("2. 確保兩台機器在同一個子網路內")
    print("3. 檢查防火牆設置，確保不會阻斷原始封包")
    print("4. 在接收端使用混雜模式可能會提高接收機率")
    print("5. 確保接收端的EtherType (0x88B5) 與發送端一致")
    s.close()

if __name__ == '__main__':
    main()