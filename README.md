# Computer Networks Homework (M11302209)

## 1. Python venv 環境建立

```bash
cd ComputerNetworksHW
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 2. Raw Socket 傳送/接收

- 啟動接收端：
  ```bash
  sudo python raw_receiver.py
  ```
- 啟動傳送端：
  ```bash
  sudo python raw_sender.py <目標IP>
  ```

## 3. IP Socket 傳送/接收

- 啟動接收端：
  ```bash
  python ip_receiver.py
  ```
- 啟動傳送端：
  ```bash
  python ip_sender.py <目標IP>
  ```

## 4. Ping 工具

- 執行：
  ```bash
  sudo python ping.py <目標IP>
  ```
- 額外功能：丟包率統計、平均延遲、TTL 設定

## 5. Traceroute 工具

- 執行：
  ```bash
  sudo python traceroute.py <目標IP>
  ```
- 額外功能：每跳延遲、地理位置查詢、最大 TTL 設定

## 6. Wireshark 封包撈取

- 使用 tshark 自動撈取：
  ```bash
  sudo python capture_packets.py <interface> <output_file.pcap>
  ```
- 例如：
  ```bash
  sudo python capture_packets.py eth0 output.pcap
  ```

## 7. 截圖與說明

- 執行各程式時，請用 Wireshark 或 capture_packets.py 撈取封包，並於 PDF 報告附上截圖與說明。


