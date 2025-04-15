import socket
import sys

def main():
    if len(sys.argv) != 2:
        print(f"用法: python {sys.argv[0]} <目標IP>")
        sys.exit(1)
    dst_ip = sys.argv[1]
    data = b'Hello from ip_sender!'
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto(data, (dst_ip, 54321))
    print(f"已送出資料到 {dst_ip}:54321")
    s.close()

if __name__ == "__main__":
    main()
