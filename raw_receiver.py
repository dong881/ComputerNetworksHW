import socket
import struct
import sys
import time
import binascii

# Windows-specific constants - use integer value directly
SIO_RCVALL = 0x98000001  # Changed from ctypes.c_ulong to int
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
        
        # Enable promiscuous mode using integer value for SIO_RCVALL
        sock.ioctl(SIO_RCVALL, 1)
    except socket.error as e:
        print(f"Socket binding error: {e}")
        sock.close()
        sys.exit(1)

def contains_protocol_signature(data):
    """Check if data contains our custom protocol signature"""
    # Convert ETH_PROTO to bytes in network byte order (big-endian)
    proto_bytes = struct.pack('!H', ETH_PROTO)
    
    # Look for the protocol bytes in the data
    return proto_bytes in data

def main():
    # Change this to your network interface's IP address
    interface_ip = "140.118.123.105"  

    # Create and configure socket
    sock = create_raw_socket()
    bind_interface(sock, interface_ip)
    
    print(f"Waiting for frames with protocol 0x{ETH_PROTO:04X}...")
    
    try:
        while True:
            # Receive a packet
            packet, addr = sock.recvfrom(BUFFER_SIZE)
            
            # Skip IP header (typically 20 bytes) to get to packet data
            ip_header_length = (packet[0] & 0x0F) * 4  # Extract header length
            data = packet[ip_header_length:]
            
            # Filter packets by our protocol signature
            if contains_protocol_signature(data):
                print(f"\nReceived {len(packet)} bytes from {addr[0]} - PROTOCOL MATCH")
                
                # Print packet details
                print(f"Data (first 64 bytes): {data[:64].hex(' ')}")
                print(f"Decoded: {data.decode('ascii', errors='ignore')[:64]}")
            
    except KeyboardInterrupt:
        print("\nExiting program...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Disable promiscuous mode
        try:
            sock.ioctl(SIO_RCVALL, 0)
        except:
            pass
        sock.close()

if __name__ == "__main__":
    main()
