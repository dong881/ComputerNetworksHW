#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <linux/if_packet.h>
#include <linux/if_ether.h>
#include <net/ethernet.h>
#include <arpa/inet.h>
#include <net/if.h>

#define ETH_PROTO 0x1234  // 需與發送端一致
#define BUFFER_SIZE 1024

int create_raw_socket() {
    int sock = socket(AF_PACKET, SOCK_RAW, htons(ETH_PROTO));
    if (sock < 0) {
        perror("socket() failed");
        exit(EXIT_FAILURE);
    }
    return sock;
}

void bind_interface(int sock, const char *iface) {
    struct ifreq ifr;
    memset(&ifr, 0, sizeof(ifr));
    strncpy(ifr.ifr_name, iface, IFNAMSIZ);

    if (setsockopt(sock, SOL_SOCKET, SO_BINDTODEVICE, &ifr, sizeof(ifr)) < 0) {
        perror("setsockopt(SO_BINDTODEVICE) failed");
        close(sock);
        exit(EXIT_FAILURE);
    }
}

int main() {
    const char *iface = "eth3";  // 修改為接收端網卡名稱

    int sock = create_raw_socket();
    bind_interface(sock, iface);

    printf("Waiting for frames...\n");
    while (1) {
        char buffer[BUFFER_SIZE];
        struct sockaddr_ll saddr;
        socklen_t saddr_len = sizeof(saddr);

        ssize_t received = recvfrom(sock, buffer, BUFFER_SIZE, 0,
                                   (struct sockaddr *)&saddr, &saddr_len);
        if (received < 0) {
            perror("recvfrom() failed");
            continue;
        }

        struct ethhdr *eth = (struct ethhdr *)buffer;
        printf("\nReceived %zd bytes\n", received);
        printf("Source MAC: %02X:%02X:%02X:%02X:%02X:%02X\n",
               eth->h_source[0], eth->h_source[1], eth->h_source[2],
               eth->h_source[3], eth->h_source[4], eth->h_source[5]);
        printf("Data: %.*s\n", (int)(received - sizeof(struct ethhdr)),
               buffer + sizeof(struct ethhdr));
    }

    close(sock);
    return 0;
}

