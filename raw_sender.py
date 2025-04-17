import socket
import struct
import sys
import array
import fcntl
import os

# For Linux only (sender stays on Linux)
SIOCGIFINDEX = 0x8933
ETH_PROTO = 0x1234  # Must match the receiver's protocol
BUFFER_SIZE = 1024

def create_raw_socket():
    """Create a raw socket for sending Ethernet frames"""
    try:
        s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(ETH_PROTO))
    except socket.error as e:
        print(f"Socket creation error: {e}")
        sys.exit(1)
    return s

def get_interface_info(iface):
    """Get the interface index and MAC address using /sys/class/net filesystem"""
    try:
        # Get interface index
        with open(f"/sys/class/net/{iface}/ifindex") as f:
            ifindex = int(f.read().strip())
        
        # Get MAC address
        with open(f"/sys/class/net/{iface}/address") as f:
            mac_str = f.read().strip()
        mac = [int(byte, 16) for byte in mac_str.split(":")]
        
        return ifindex, mac
    except Exception as e:
        print(f"Error getting interface info: {e}")
        print(f"Make sure interface '{iface}' exists and you have required permissions")
        raise

def main():
    # Interface name - modify as needed
    iface = "eno1"
    
    # Destination MAC - modify to match the target device
    dest_mac = [0x18, 0x31, 0xbf, 0x93, 0x7a, 0x80]
    
    # Create socket and get interface info
    sock = create_raw_socket()
    ifindex, src_mac = get_interface_info(iface)
    
    # Construct Ethernet frame
    # Destination MAC (6 bytes) + Source MAC (6 bytes) + EtherType (2 bytes)
    header = struct.pack('!6B6BH', 
                         dest_mac[0], dest_mac[1], dest_mac[2], 
                         dest_mac[3], dest_mac[4], dest_mac[5],
                         src_mac[0], src_mac[1], src_mac[2], 
                         src_mac[3], src_mac[4], src_mac[5],
                         ETH_PROTO)
    
    # Data payload
    data = b"Hello from sender!"
    
    # Complete frame
    packet = header + data
    
    # Send the frame
    try:
        # Set up the address structure for sendto
        address = (iface, 0)
        bytes_sent = sock.sendto(packet, address)
        
        print(f"Sent {bytes_sent} bytes to MAC {':'.join(f'{x:02X}' for x in dest_mac)}")
        print(f"From interface {iface} (ifindex: {ifindex})")
        print(f"Source MAC: {':'.join(f'{x:02X}' for x in src_mac)}")
    except socket.error as e:
        print(f"Failed to send: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    main()
