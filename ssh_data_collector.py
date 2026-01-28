"""
SSH Data Collector

Demonstrates:
- SSH automation with Paramiko
- Command output parsing
- Data aggregation and Excel export
- Secure credential handling via environment variables
"""

import paramiko
import pandas as pd
import re
import time
import os


# SSH 連線資訊（使用環境變數）
HOSTNAME = os.getenv("SSH_HOST")
PORT = int(os.getenv("SSH_PORT", 22))
USERNAME = os.getenv("SSH_USER")
PASSWORD = os.getenv("SSH_PASSWORD")

if not all([HOSTNAME, USERNAME, PASSWORD]):
    raise EnvironmentError("請先設定 SSH_HOST / SSH_USER / SSH_PASSWORD 環境變數")


# 命令設定
COMMANDS = {
    "COMMAND_DATE": False,
    "COMMAND_MEMORY": True,
    "COMMAND_CPU": True,
    "COMMAND_VERSION": True,
    "COMMAND_SYSTEM_TIME": True,
}

# 需要從指令輸出中擷取的關鍵字
KEYWORDS = ["keyword1", "keyword2", "keyword3", "keyword4"]

# 輸出 Excel 的欄位名稱（對應 COMMANDS 的順序）
HEADERS = ["Date", "Memory", "CPU", "Version", "System Time"]

OUTPUT_FILE = "Sample_Output.xlsx"
SHEET_NAME = "TEST_SHEET_NAME"

# 建立 SSH 連線
def connect_ssh():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=HOSTNAME,
        port=PORT,
        username=USERNAME,
        password=PASSWORD,
        timeout=10
    )
    return client

#透過 invoke_shell() 發送指令並取得輸出
def execute_command(shell, command, wait_time=3):
    shell.send(command + "\n")
    time.sleep(wait_time)
    return shell.recv(65535).decode(errors="ignore")

#從指令輸出中：
    #1. 找出包含關鍵字的行
    #2. 擷取關鍵字後的內容
def filter_output(output):
    results = []
    for line in output.splitlines():
        for keyword in KEYWORDS:
            match = re.search(keyword, line)
            if match:
                content = line[match.end():].strip().strip('"')
                # 若為百分比，轉為 0~1 的浮點數
                try:
                    if "%" in content:
                        value = float(content.strip("%")) / 100
                    else:
                        value = float(content)
                except ValueError:
                     # 若無法轉換為數字，保留原字串
                    value = content
                results.append(value)
                break
    return results

#建立 SSH 連線與 shell
def main():
    client = connect_ssh()
    shell = client.invoke_shell()
    
    # 儲存每個指令的處理結果
    results = {}

    for command, need_filter in COMMANDS.items():
        output = execute_command(shell, command)

        if need_filter:
            results[command] = filter_output(output)
        else:
            lines = output.strip().splitlines()
            results[command] = [line.strip() for line in lines[1:-1]]
    #關閉 SSH 連線
    shell.close()
    client.close()

    # 將結果整理成 DataFrame
    # 補齊每一欄的資料長度，避免欄位長度不同
    max_len = max(len(v) for v in results.values())
    data = {
        HEADERS[i]: (results[list(results.keys())[i]] + [""] * max_len)[:max_len]
        for i in range(len(HEADERS))
    }

    df = pd.DataFrame(data)
    # 若 Excel 已存在則追加資料
    if os.path.exists(OUTPUT_FILE):
        old_df = pd.read_excel(OUTPUT_FILE)
        df = pd.concat([old_df, df], ignore_index=True)

    df.to_excel(OUTPUT_FILE, sheet_name=SHEET_NAME, index=False)
    print(f"輸出完成：{OUTPUT_FILE}")

# 確保此檔案被 import 時不會自動執行
if __name__ == "__main__":
    main()
