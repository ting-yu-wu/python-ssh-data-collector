# SSH Command Collector (Python)

此專案展示我使用 Python 進行：
- SSH 自動化操作（Paramiko）
- 指令輸出解析（Regex）
- 資料整理與 Excel 匯出（Pandas）
- 基本資安概念（環境變數管理帳密）

> 本專案為示範用途，未包含任何真實設備資訊。

## Tech Stack
- Python
- Paramiko
- Pandas


## How It Works
1. 透過 SSH 連線到遠端設備
2. 依序執行多個指令
3. 依關鍵字解析指令輸出
4. 將結果整理並輸出成 Excel


## Security
- SSH 帳號密碼皆使用環境變數
- 程式碼中未硬編任何敏感資訊


## Note
本專案主要展示程式結構設計與實作能力，
實際指令內容可依設備類型調整。
