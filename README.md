# chrome_extension_with_yt-dlp

使用 Chrome 擴充功能（Manifest V3）搭配 Native Messaging，呼叫本機 Python 腳本執行 `yt-dlp` 下載目前頁面影片。

## 目錄結構

```text
chrome_extension_with_yt-dlp/
├─ README.md
├─ plan.md
├─ chrome-extension/
│  ├─ manifest.json
│  ├─ popup.html
│  ├─ popup.js
│  └─ background.js
└─ native-host/
   ├─ host.py
   ├─ run_host.bat
   ├─ host_manifest.json
   └─ install.bat
```

## 檔案說明

### 1) `chrome-extension/manifest.json`
- 使用 Manifest V3
- 權限：`activeTab`、`nativeMessaging`、`tabs`
- 指定 `popup.html` 與 `background.js`

### 2) `chrome-extension/popup.html`
- 一個按鈕：**下載當前影片**
- 顯示簡單狀態訊息

### 3) `chrome-extension/popup.js`
- 取得目前分頁 URL
- 傳送訊息給 background service worker

### 4) `chrome-extension/background.js`
- 接收 popup 訊息
- 呼叫 `chrome.runtime.sendNativeMessage('com.ytdlp.downloader', { url })`

### 5) `native-host/host.py`
- 正確實作 Native Messaging 的 4-byte little-endian header 讀寫
- 從 stdin 讀取 JSON，解析 `url`
- 用 `subprocess.Popen(['yt-dlp', url], cwd=Downloads)` 背景啟動下載
- 透過 stdout 回傳 JSON 給擴充功能

### 5.1) `native-host/run_host.bat`
- Windows 上 Chrome Native Messaging 只能啟動 `.exe`/`.bat`/`.cmd`
- 此檔為包裝器，呼叫 `python host.py`
- `host_manifest.json` 的 `path` 必須指向此檔案

### 6) `native-host/host_manifest.json`
- Native Messaging host 設定檔
- 請手動更新：
  - `path`：改成你電腦上的 `host.py` 絕對路徑
  - `allowed_origins`：改成你的 Chrome 擴充功能 ID

### 7) `native-host/install.bat`
- 雙擊即可把 `host_manifest.json` 路徑註冊到：
  - `HKCU\Software\Google\Chrome\NativeMessagingHosts\com.ytdlp.downloader`

## 安裝與測試步驟（Windows）

1. **準備 Native Host 設定**
   - 編輯 `native-host/host_manifest.json`
   - 將 `path` 改成 `run_host.bat` 的絕對路徑

2. **載入擴充功能**
   - 開啟 `chrome://extensions`
   - 開啟「開發人員模式」
   - 點「載入未封裝項目」，選擇 `chrome-extension/` 資料夾
   - 複製擴充功能 ID

3. **設定 allowed_origins**
   - 回到 `native-host/host_manifest.json`
   - 將 `chrome-extension://__REPLACE_WITH_YOUR_EXTENSION_ID__/` 換成實際 ID

4. **執行註冊批次檔**
   - 雙擊 `native-host/install.bat`
   - 看到 `[OK]` 代表已寫入登錄檔

5. **實際下載測試**
   - 開啟任一影片頁面（例如 YouTube）
   - 點擊擴充功能圖示 → 按「下載當前影片」
   - 檢查 `Downloads` 資料夾是否開始下載

## 注意事項
- 請確認 `yt-dlp` 與 `ffmpeg` 可在命令列直接執行。
- `chrome://` 等特殊頁面不會提供一般可下載網址。
- 若無反應，請檢查：
  - `host_manifest.json` 的 `path` 是否正確
  - `allowed_origins` 是否為目前擴充功能 ID
  - Registry 是否存在正確鍵值
