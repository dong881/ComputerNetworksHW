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
    while ttl <= max_hops:
        recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        send_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
        recv_socket.settimeout(timeout)
        recv_socket.bind(("", port))
        send_time = time.time()
        send_socket.sendto(b"", (dest_addr, port))
        curr_addr = None
        try:
            _, curr_addr = recv_socket.recvfrom(512)
            recv_time = time.time()
            curr_addr = curr_addr[0]
            rtt = (recv_time - send_time) * 1000
        except socket.timeout:
            rtt = None
        finally:
            send_socket.close()
            recv_socket.close()
        if curr_addr:
            country, region, city = get_geolocation(curr_addr)
            geo = f" [{country} {region} {city}]" if country or region or city else ""
            print(f"{ttl}\t{curr_addr}{geo}\t{f'{rtt:.2f} ms' if rtt else '*'}")
        else:
            print(f"{ttl}\t*\t*")
        ttl += 1
        if curr_addr == dest_addr:
            break

def main():
    import argparse
    parser = argparse.ArgumentParser(description='自製 traceroute 工具 (含每跳延遲/地理位置/最大TTL)')
    parser.add_argument('host', help='目標主機')
    parser.add_argument('--max-ttl', type=int, default=30, help='最大 TTL 數值')
    args = parser.parse_args()
    traceroute(args.host, max_hops=args.max_ttl)

if __name__ == '__main__':
    main()
