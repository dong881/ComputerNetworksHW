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
#include <sys/ioctl.h>  // 新增此標頭檔

#define ETH_PROTO 0x1234  // 自定義協定類型（兩端需一致）
#define BUFFER_SIZE 1024

int create_raw_socket() {
    int sock = socket(AF_PACKET, SOCK_RAW, htons(ETH_PROTO));
    if (sock < 0) {
        perror("socket() failed");
        exit(EXIT_FAILURE);
    }
    return sock;
}

void get_interface_info(int sock, const char *iface, int *ifindex, unsigned char *mac) {
    struct ifreq ifr;
    memset(&ifr, 0, sizeof(ifr));
    strncpy(ifr.ifr_name, iface, IFNAMSIZ);

    if (ioctl(sock, SIOCGIFINDEX, &ifr) < 0) {
        perror("ioctl(SIOCGIFINDEX) failed");
        close(sock);
        exit(EXIT_FAILURE);
    }
    *ifindex = ifr.ifr_ifindex;

    if (ioctl(sock, SIOCGIFHWADDR, &ifr) < 0) {
        perror("ioctl(SIOCGIFHWADDR) failed");
        close(sock);
        exit(EXIT_FAILURE);
    }
    memcpy(mac, ifr.ifr_hwaddr.sa_data, ETH_ALEN);
}

int main() {
    const char *iface = "eno1";  // 修改為發送端網卡名稱
    unsigned char dest_mac[ETH_ALEN] = {0x18,0x31,0xbf,0x93,0x7a,0x80}; // 修改為接收端MAC
    unsigned char src_mac[ETH_ALEN];
    int ifindex;

    int sock = create_raw_socket();
    get_interface_info(sock, iface, &ifindex, src_mac);

    // 構造乙太網幀
    char buffer[BUFFER_SIZE];
    struct ethhdr *eth = (struct ethhdr *)buffer;
    memcpy(eth->h_dest, dest_mac, ETH_ALEN);
    memcpy(eth->h_source, src_mac, ETH_ALEN);
    eth->h_proto = htons(ETH_PROTO);

    // 填充數據
    const char *data = "Hello from sender!";
    strncpy(buffer + sizeof(struct ethhdr), data, strlen(data));

    // 發送幀
    struct sockaddr_ll saddr = {
        .sll_family = AF_PACKET,
        .sll_protocol = htons(ETH_PROTO),
        .sll_ifindex = ifindex,
        .sll_halen = ETH_ALEN,
    };
    memcpy(saddr.sll_addr, dest_mac, ETH_ALEN);

    ssize_t sent = sendto(sock, buffer, sizeof(struct ethhdr) + strlen(data), 0,
                         (struct sockaddr *)&saddr, sizeof(saddr));
    if (sent < 0) {
        perror("sendto() failed");
    } else {
        printf("Sent %zd bytes to MAC %02X:%02X:%02X:%02X:%02X:%02X\n",
               sent, dest_mac[0], dest_mac[1], dest_mac[2],
               dest_mac[3], dest_mac[4], dest_mac[5]);
    }

    close(sock);
    return 0;
}

