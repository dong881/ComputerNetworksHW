import os
import sys
import socket
import struct
import time
import select
import requests

def get_geolocation(ip):
    try:
        r = requests.get(f"https://ipinfo.io/{ip}/json", timeout=2)
        data = r.json()
        return data.get('country', ''), data.get('region', ''), data.get('city', '')
    except Exception:
        return '', '', ''

def traceroute(dest_name, max_hops=30, timeout=2):
    dest_addr = socket.gethostbyname(dest_name)
    print(f"traceroute to {dest_name} ({dest_addr}), {max_hops} hops max")
    port = 33434
    ttl = 1
    
    # 準備收集結果的列表，用於顯示統計資訊
    results = []
    
    while ttl <= max_hops:
        recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        send_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
        recv_socket.settimeout(timeout)
        recv_socket.bind(("", port))
        
        # 進行三次嘗試來提高準確性
        tries = 3
        rtts = []
        curr_addr = None
        
        for i in range(tries):
            send_time = time.time()
            send_socket.sendto(b"", (dest_addr, port))
            try:
                _, curr_addr_info = recv_socket.recvfrom(512)
                recv_time = time.time()
                if not curr_addr:  # 只在第一次成功取得回應時設定 curr_addr
                    curr_addr = curr_addr_info[0]
                rtts.append((recv_time - send_time) * 1000)
            except socket.timeout:
                rtts.append(None)
                
        send_socket.close()
        recv_socket.close()
        
        # 計算平均延遲 (忽略 timeout)
        valid_rtts = [rtt for rtt in rtts if rtt is not None]
        avg_rtt = sum(valid_rtts) / len(valid_rtts) if valid_rtts else None
        
        if curr_addr:
            country, region, city = get_geolocation(curr_addr)
            geo = f" [{country} {region} {city}]" if country or region or city else ""
            rtt_str = f"{avg_rtt:.2f} ms" if avg_rtt is not None else "*"
            print(f"{ttl}\t{curr_addr}{geo}\t{rtt_str}")
            results.append((ttl, curr_addr, geo, avg_rtt))
        else:
            print(f"{ttl}\t*\t*")
            results.append((ttl, None, "", None))
            
        ttl += 1
        if curr_addr == dest_addr:
            break
    
    # 顯示統計資訊
    print("\n--- traceroute 統計 ---")
    print(f"路徑總跳數: {len(results)}")
    successful_hops = [r for r in results if r[1] is not None]
    print(f"成功率: {len(successful_hops)}/{len(results)} ({len(successful_hops)/len(results)*100:.1f}%)")
    
    # 顯示有地理位置資訊的跳數
    geo_hops = [r for r in results if r[2]]
    if geo_hops:
        print(f"經過的國家/地區: {', '.join(set([r[2].strip('[]') for r in geo_hops]))}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='自製 traceroute 工具 (含每跳延遲/地理位置/最大TTL)')
    parser.add_argument('host', help='目標主機')
    parser.add_argument('--max-ttl', type=int, default=30, help='最大 TTL 數值')
    args = parser.parse_args()
    traceroute(args.host, max_hops=args.max_ttl)

if __name__ == '__main__':
    main()
