import os
import sys
import time
import socket
import struct
import select

ICMP_ECHO_REQUEST = 8

def checksum(source_string):
    sum = 0
    countTo = (len(source_string) // 2) * 2
    count = 0
    while count < countTo:
        thisVal = source_string[count + 1] * 256 + source_string[count]
        sum = sum + thisVal
        sum = sum & 0xffffffff
        count = count + 2
    if countTo < len(source_string):
        sum = sum + source_string[len(source_string) - 1]
        sum = sum & 0xffffffff
    sum = (sum >> 16) + (sum & 0xffff)
    sum = sum + (sum >> 16)
    answer = ~sum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

def create_packet(id, seq, ttl, payload_size=56):
    header = struct.pack('bbHHh', ICMP_ECHO_REQUEST, 0, 0, id, seq)
    data = bytes((192 + (x % 64) for x in range(payload_size)))
    my_checksum = checksum(header + data)
    header = struct.pack('bbHHh', ICMP_ECHO_REQUEST, 0, socket.htons(my_checksum), id, seq)
    return header + data

def ping(dest_addr, count=4, timeout=1, ttl=64):
    try:
        dest_ip = socket.gethostbyname(dest_addr)
    except socket.gaierror:
        print(f"無法解析主機: {dest_addr}")
        return
    print(f"PING {dest_addr} ({dest_ip}) with TTL={ttl}")
    stats = {'sent': 0, 'recv': 0, 'rtt': []}
    for seq in range(count):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
            s.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
        except PermissionError:
            print("請用 sudo 執行本程式！")
            return
        packet_id = os.getpid() & 0xFFFF
        packet = create_packet(packet_id, seq, ttl)
        send_time = time.time()
        s.sendto(packet, (dest_ip, 1))
        stats['sent'] += 1
        ready = select.select([s], [], [], timeout)
        if ready[0] == []:
            print(f"Request timeout for icmp_seq {seq}")
            continue
        recv_packet, addr = s.recvfrom(1024)
        recv_time = time.time()
        icmp_header = recv_packet[20:28]
        type, code, checksum_recv, p_id, sequence = struct.unpack('bbHHh', icmp_header)
        if p_id == packet_id:
            rtt = (recv_time - send_time) * 1000
            stats['recv'] += 1
            stats['rtt'].append(rtt)
            print(f"{len(recv_packet)} bytes from {addr[0]}: icmp_seq={seq} ttl={ttl} time={rtt:.2f} ms")
        s.close()
        time.sleep(1)
    print(f"\n--- {dest_addr} ping statistics ---")
    loss = (stats['sent'] - stats['recv']) / stats['sent'] * 100
    print(f"{stats['sent']} packets transmitted, {stats['recv']} received, {loss:.1f}% packet loss")
    if stats['rtt']:
        print(f"rtt min/avg/max = {min(stats['rtt']):.2f}/{sum(stats['rtt'])/len(stats['rtt']):.2f}/{max(stats['rtt']):.2f} ms")
    print("(可用 --ttl <數值> 設定 TTL)")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='自製 ping 工具 (含丟包率/平均延遲/TTL 設定)')
    parser.add_argument('host', help='目標主機')
    parser.add_argument('-c', '--count', type=int, default=4, help='封包數')
    parser.add_argument('--ttl', type=int, default=64, help='TTL 數值')
    args = parser.parse_args()
    ping(args.host, count=args.count, ttl=args.ttl)

if __name__ == '__main__':
    main()
