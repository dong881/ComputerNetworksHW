import socket

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("0.0.0.0", 54321))
    print("等待接收資料...")
    while True:
        data, addr = s.recvfrom(1024)
        print(f"收到來自 {addr[0]} 的資料: {data}")

if __name__ == "__main__":
    main()
