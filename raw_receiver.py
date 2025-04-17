import socket
import struct
import sys
import ctypes
import time

# Windows-specific constants
SIO_RCVALL = ctypes.c_ulong(0x98000001)
ETH_PROTO = 0x1234  # Match the sender's protocol
BUFFER_SIZE = 65535  # Larger buffer for safety

def create_raw_socket():
    """Create a raw socket for packet capture"""
    try:
        # Create raw socket for IP packets
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
    except socket.error as e:
        print(f"Socket creation error: {e}")
        print("Note: This program must run with administrator privileges")
        sys.exit(1)
    return s

def bind_interface(sock, interface_ip):
    """Bind socket to the specified network interface"""
    try:
        # Bind to the interface
        sock.bind((interface_ip, 0))
        
        # Enable promiscuous mode
        sock.ioctl(SIO_RCVALL, 1)
    except socket.error as e:
        print(f"Socket binding error: {e}")
        sock.close()
        sys.exit(1)

def main():
    # Change this to your network interface's IP address
    interface_ip = "192.168.1.100"  

    # Create and configure socket
    sock = create_raw_socket()
    bind_interface(sock, interface_ip)
    
    print("Waiting for frames...")
    
    try:
        while True:
            # Receive a packet
            packet, addr = sock.recvfrom(BUFFER_SIZE)
            
            # Skip IP header (typically 20 bytes) to get to packet data
            ip_header_length = (packet[0] & 0x0F) * 4  # Extract header length
            data = packet[ip_header_length:]
            
            # Print packet information
            print(f"\nReceived {len(packet)} bytes")
            print(f"Source IP: {addr[0]}")
            print(f"Data: {data.decode('ascii', errors='ignore')}")
            
    except KeyboardInterrupt:
        print("\nExiting program...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Disable promiscuous mode
        sock.ioctl(SIO_RCVALL, 0)
        sock.close()

if __name__ == "__main__":
    main()
