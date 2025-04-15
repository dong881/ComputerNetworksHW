import socket
import sys
import binascii
import struct
import time
import subprocess

def mac_str_to_bytes(mac):
    return binascii.unhexlify(mac.replace(':', ''))

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
    # 如果指定了目標MAC，則使用；否則使用默認的接收者MAC
    if len(sys.argv) == 3:
        dst_mac = sys.argv[2]
    else:
        dst_mac = "94:c6:91:a9:5d:26"  # 更新為接收者的實際 MAC
    
    # 在開始前，檢查網路連通性
    receiver_ip = "140.118.123.107"  # 接收端IP地址
    if not check_network_route(receiver_ip):
        print(f"警告: 無法 ping 通接收端 {receiver_ip}")
        print("Layer 2 封包只能在同一個網段內傳送，不能跨越路由器")
        if input("是否仍要嘗試發送? (y/n): ").lower() != 'y':
            sys.exit(1)
    
    # 嘗試使用廣播地址，增加被接收機會
    use_broadcast = False
    if len(sys.argv) < 3 and input("是否嘗試使用廣播地址? (y/n): ").lower() == 'y':
        dst_mac = "ff:ff:ff:ff:ff:ff"
        use_broadcast = True
        print("使用廣播地址發送封包")
    
    ether_type = 0x88B5  # 自訂 EtherType
    
    # 構建以太網幀
    dst_mac_bytes = mac_str_to_bytes(dst_mac)
    src_mac_bytes = b'\x00\x00\x00\x00\x00\x00'  # 系統會自動填充
    
    # 創建並發送
    s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
    s.bind((interface, 0))
    
    # 發送多個封包，增加接收機會
    for i in range(10):  # 增加發送次數
        payload = f"Hello Layer2 Only! Packet #{i+1}".encode()
        # 確保封包大小適中
        payload = payload.ljust(50, b' ')  # 確保有一定大小但不超過MTU
        frame = dst_mac_bytes + src_mac_bytes + struct.pack('!H', ether_type) + payload
        s.send(frame)
        print(f"發送第 {i+1} 個封包...")
        time.sleep(0.5)  # 縮短間隔，更密集發送
    
    # 取得實際發送的 MAC 地址
    src_mac_actual = ':'.join(f'{b:02x}' for b in bytes.fromhex(s.getsockname()[4].hex()))
    print(f"已送出Layer2乙太網路幀")
    print(f"發送者 MAC: {src_mac_actual}")
    print(f"接收者 MAC: {dst_mac}")
    print(f"EtherType: 0x{ether_type:04X}")
    if use_broadcast:
        print("廣播封包已發送，任何監聽的機器都可能收到")
    print("提示: 如果仍無法接收，請確保兩台機器直接連接或在同一個交換機上，不能有路由器分隔")
    print(f"提示: 請確保發送和接收的機器位於同一網段，且使用相同的EtherType")
    s.close()

if __name__ == '__main__':
    main()