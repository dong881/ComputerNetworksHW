import sys
import subprocess
import time

def main():
    if len(sys.argv) != 3:
        print(f"用法: sudo python {sys.argv[0]} <interface> <output_file.pcap>")
        sys.exit(1)
    interface = sys.argv[1]
    output_file = sys.argv[2]
    print(f"開始撈取 {interface} 封包，儲存到 {output_file} (Ctrl+C 停止)")
    try:
        subprocess.run([
            'tshark', '-i', interface, '-w', output_file
        ])
    except KeyboardInterrupt:
        print("\n已停止撈取")
    except Exception as e:
        print(f"錯誤: {e}")

if __name__ == '__main__':
    main()
