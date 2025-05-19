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
- 參數說明：
  ```
  --count <數值>    指定發送的封包數量
  --ttl <數值>      指定 TTL 數值
  ```

## 5. Traceroute 工具

- 執行：
  ```bash
  sudo python traceroute.py <目標IP>
  ```
- 額外功能：每跳延遲、地理位置查詢、最大 TTL 設定
- 增強功能：三次測試取平均、路徑統計資訊
- 參數說明：
  ```
  --max-ttl <數值>  指定最大 TTL 數值
  ```

## 6. UE 頻段鎖定工具

- 執行：
  ```bash
  ./modify_UE.sh lock_frequency [指令] [日誌檔案] [頻率]
  ```
- 指令說明：
  ```
  check           - 查詢當前頻段鎖定狀態
  lock [頻率]     - 鎖定指定頻率 (預設 630048)
  unlock          - 解除頻段鎖定
  ```
- 例如：
  ```bash
  ./modify_UE.sh lock_frequency check
  ./modify_UE.sh lock_frequency lock "" 649920
  ./modify_UE.sh lock_frequency unlock
  ```

## 7. Wireshark 封包撈取

- 使用 tshark 自動撈取：
  ```bash
  sudo python capture_packets.py <interface> <output_file.pcap>
  ```
- 例如：
  ```bash
  sudo python capture_packets.py eth0 output.pcap
  ```

## 8. 截圖與說明

- 執行各程式時，請用 Wireshark 或 capture_packets.py 撈取封包，並於 PDF 報告附上截圖與說明。


