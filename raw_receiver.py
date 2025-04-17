import socket
import struct
import sys
import time
import binascii
import re

# Windows-specific constants
SIO_RCVALL = 0x98000001
ETH_PROTO = 0x1234  # Must match the sender's protocol (0x1234)
BUFFER_SIZE = 65535

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
    # Change this to your actual network interface's IP address
    interface_ip = "192.168.1.100"  # IMPORTANT: Update this with your actual IP!
    
    print(f"Starting raw packet receiver to capture protocol 0x{ETH_PROTO:04X} packets")
    print(f"Listening on interface: {interface_ip}")

    # Create and configure socket
    sock = create_raw_socket()
    bind_interface(sock, interface_ip)
    
    print("Waiting for frames... Press Ctrl+C to exit")
    
    try:
        while True:
            # Receive a packet
            packet, addr = sock.recvfrom(BUFFER_SIZE)
            
            # Convert the full packet to hex for inspection
            hex_data = binascii.hexlify(packet).decode('ascii')
            
            # Look for our protocol signature (0x1234) in the hex data
            # In hex: 12 34
            if re.search(r'(?:12.?34|34.?12)', hex_data):
                print("\n" + "="*50)
                print(f"Potential protocol match found from IP: {addr[0]}")
                print(f"Full packet length: {len(packet)} bytes")
                
                # Print packet in hexadecimal format with ASCII representation
                print("\nHex dump:")
                for i in range(0, len(packet), 16):
                    chunk = packet[i:i+16]
                    hex_line = ' '.join(f'{b:02x}' for b in chunk)
                    ascii_line = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)
                    print(f"{i:04x}: {hex_line:<48} |{ascii_line}|")
                
                # Try to extract the data portion
                try:
                    # Skip IP header (first byte & 0x0F gives the header length in 32-bit words)
                    ip_header_len = (packet[0] & 0x0F) * 4
                    data = packet[ip_header_len:]
                    print(f"\nData portion (ASCII): {data.decode('ascii', errors='ignore')}")
                except Exception as e:
                    print(f"Error decoding data: {e}")
                
                print("="*50)
            
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
        print("Socket closed")

if __name__ == "__main__":
    main()
