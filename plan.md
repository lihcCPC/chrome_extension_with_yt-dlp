# Chrome Extension + yt-dlp Native Messaging 規劃

## 目標
建立一個最小可用的 Chrome 擴充功能（Manifest V3），透過 Native Messaging 呼叫本機 Python 腳本，使用 `yt-dlp` 下載目前分頁影片。

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
   ├─ run_host.bat        ← Windows 用包裝器（Chrome 無法直接執行 .py）
   ├─ host_manifest.json
   └─ install.bat
```

---

## 第一部分：Chrome 擴充功能端 (Manifest V3)

### 1. `manifest.json`
- manifest_version: 3
- 權限：`activeTab`、`nativeMessaging`、`tabs`
- `action.default_popup` → `popup.html`
- `background.service_worker` → `background.js`

### 2. `popup.html`
- 一個按鈕「下載當前影片」
- 一個 `<div id="status">` 顯示執行結果
- 引入 `popup.js`

### 3. `popup.js`
- 點按鈕時：
  1. 用 `chrome.tabs.query` 取得當前分頁 URL
  2. 驗證是否為 `http(s)://` 開頭
  3. 透過 `chrome.runtime.sendMessage` 傳送 `{ type: 'DOWNLOAD_CURRENT_VIDEO', url }` 給 background
  4. 顯示回傳結果或錯誤

### 4. `background.js` (Service Worker)
- 監聽 `chrome.runtime.onMessage`
- 收到 `DOWNLOAD_CURRENT_VIDEO` 時呼叫：
  ```js
  chrome.runtime.sendNativeMessage('com.ytdlp.downloader', { url }, callback)
  ```
- 回傳 `{ ok, message/error }` 給 popup
- 使用 `return true` 保持 async channel

---

## 第二部分：本機 Python 端 (Native Messaging Host)

### 5. `host.py`
- **stdin 讀取**：先讀 4 bytes（little-endian unsigned int），得到 message 長度，再讀取該長度的 JSON payload
- **stdout 寫入**：將 JSON 回應 encode 為 UTF-8，先寫 4-byte 長度 header，再寫 payload
- 收到 `{ "url": "..." }` 後，用 `subprocess.Popen(['yt-dlp', url], cwd=Downloads)` 背景啟動下載
- Windows 上加 `creationflags=CREATE_NO_WINDOW` 避免彈出黑窗
- 回傳 `{ "ok": true, "message": "已開始下載：..." }`

### 6. `run_host.bat`（Windows 包裝器）
- Chrome Native Messaging 在 Windows 上只能啟動 `.exe`/`.bat`/`.cmd`
- 內容：`python "%~dp0host.py"`
- `host_manifest.json` 的 `path` 必須指向此 `.bat` 而非 `.py`

---

## 第三部分：Windows 系統註冊端

### 7. `host_manifest.json`
```json
{
  "name": "com.ytdlp.downloader",
  "description": "Native host for launching yt-dlp downloads",
  "path": "<run_host.bat 的絕對路徑>",
  "type": "stdio",
  "allowed_origins": ["chrome-extension://<YOUR_EXTENSION_ID>/"]
}
```
- `path`：必須是 `run_host.bat` 的完整絕對路徑
- `allowed_origins`：載入擴充功能後取得的 ID

### 8. `install.bat`
- 用 `reg add` 寫入登錄檔：
  ```
  HKCU\Software\Google\Chrome\NativeMessagingHosts\com.ytdlp.downloader
  ```
- 預設值 (REG_SZ) 設為 `host_manifest.json` 的絕對路徑
- 使用 `%~dp0` 自動取得當前資料夾路徑

---

## 操作測試步驟

### 前置需求
- Windows 10/11
- Chrome 瀏覽器
- Python 3.8+（且 `python` 在 PATH 中）
- `yt-dlp` 已安裝（`pip install yt-dlp`）且可在命令列執行
- 建議安裝 `ffmpeg`（合併影音用）

### Step 1：編輯 host_manifest.json
1. 將 `path` 改為 `run_host.bat` 的實際絕對路徑，例如：
   ```
   D:\\git_proj\\chrome_extension_with_yt-dlp\\native-host\\run_host.bat
   ```

### Step 2：載入 Chrome 擴充功能
1. 開啟 `chrome://extensions`
2. 右上角開啟「開發人員模式」
3. 點「載入未封裝項目」→ 選擇 `chrome-extension/` 資料夾
4. 記下產生的 **擴充功能 ID**

### Step 3：填入 allowed_origins
1. 回到 `host_manifest.json`
2. 把 `__REPLACE_WITH_YOUR_EXTENSION_ID__` 替換為實際 ID

### Step 4：執行 install.bat
1. 雙擊 `native-host/install.bat`
2. 看到 `[OK]` 即代表登錄檔已寫入成功

### Step 5：測試下載
1. 開啟任一影片頁面（如 YouTube）
2. 點擊瀏覽器右上角的擴充功能圖示
3. 按「下載當前影片」
4. 狀態顯示「已送出下載命令」→ 至 `Downloads` 資料夾確認

### 疑難排解
- **無反應**：檢查 `host_manifest.json` 的 `path` 和 `allowed_origins`
- **找不到 python**：確認 `python` 在系統 PATH 中
- **yt-dlp 錯誤**：在命令列手動執行 `yt-dlp <url>` 確認可正常下載
- **Registry 問題**：執行 `reg query "HKCU\Software\Google\Chrome\NativeMessagingHosts\com.ytdlp.downloader"` 確認鍵值存在
