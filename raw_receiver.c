#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <winsock2.h>
#include <windows.h>
#include <ws2tcpip.h>
#include <iphlpapi.h>

#pragma comment(lib, "ws2_32.lib")
#pragma comment(lib, "iphlpapi.lib")

#define ETH_PROTO 0x1234  // 需與發送端一致
#define BUFFER_SIZE 1024
#define ETH_ALEN 6  // MAC address length

// Define Ethernet header structure since we don't have linux/if_ether.h
struct eth_header {
    unsigned char h_dest[ETH_ALEN];    // destination MAC
    unsigned char h_source[ETH_ALEN];  // source MAC
    unsigned short h_proto;            // protocol ID
};

int create_raw_socket() {
    // Create a raw socket
    int sock = socket(AF_INET, SOCK_RAW, IPPROTO_IP);
    if (sock == INVALID_SOCKET) {
        printf("socket() failed: %d\n", WSAGetLastError());
        WSACleanup();
        exit(EXIT_FAILURE);
    }
    return sock;
}

void bind_interface(int sock, const char *interface_ip) {
    // Bind to specific interface
    struct sockaddr_in saddr;
    memset(&saddr, 0, sizeof(saddr));
    saddr.sin_family = AF_INET;
    saddr.sin_addr.s_addr = inet_addr(interface_ip);
    saddr.sin_port = htons(0);

    if (bind(sock, (struct sockaddr *)&saddr, sizeof(saddr)) == SOCKET_ERROR) {
        printf("bind() failed: %d\n", WSAGetLastError());
        closesocket(sock);
        WSACleanup();
        exit(EXIT_FAILURE);
    }

    // Set socket to promiscuous mode
    DWORD dwValue = 1;
    if (ioctlsocket(sock, SIO_RCVALL, &dwValue) == SOCKET_ERROR) {
        printf("ioctlsocket(SIO_RCVALL) failed: %d\n", WSAGetLastError());
        closesocket(sock);
        WSACleanup();
        exit(EXIT_FAILURE);
    }
}

int main() {
    // Initialize Winsock
    WSADATA wsaData;
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
        printf("WSAStartup failed: %d\n", WSAGetLastError());
        return EXIT_FAILURE;
    }

    // Use your network interface IP instead of interface name
    const char *interface_ip = "192.168.1.100";  // 修改為接收端網卡IP

    int sock = create_raw_socket();
    bind_interface(sock, interface_ip);

    printf("Waiting for frames...\n");
    while (1) {
        char buffer[BUFFER_SIZE];
        struct sockaddr_in saddr;
        int saddr_len = sizeof(saddr);

        // Receive packet
        ssize_t received = recvfrom(sock, buffer, BUFFER_SIZE, 0, 
                                   (struct sockaddr *)&saddr, &saddr_len);
        if (received == SOCKET_ERROR) {
            printf("recvfrom() failed: %d\n", WSAGetLastError());
            continue;
        }

        // Process IP packet to extract Ethernet frame data
        // Note: Windows raw sockets receive IP packets, not Ethernet frames
        // We need to look for our custom protocol in the payload
        
        // Check if the packet contains our custom protocol (simplified approach)
        // In a real implementation, you'd need more sophisticated packet parsing
        const char *data = buffer + 20;  // Skip IP header (typically 20 bytes)
        printf("\nReceived %zd bytes\n", received);
        printf("Source IP: %s\n", inet_ntoa(saddr.sin_addr));
        printf("Data: %.*s\n", (int)(received - 20), data);
    }

    closesocket(sock);
    WSACleanup();
    return 0;
}

