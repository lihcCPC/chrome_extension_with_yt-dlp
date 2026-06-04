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
   ├─ host_manifest.json
   └─ install.bat
```

## 實作步驟
1. 建立 Chrome extension 端檔案（UI + 訊息傳遞 + Native Messaging 呼叫）。
2. 建立 Python host 並正確實作 4-byte length header stdin/stdout 協定。
3. 建立 Windows host manifest 與一鍵註冊 `install.bat`。
4. 更新 README 初版：專案說明、檔案內容、安裝與測試流程。
5. 進行基礎語法與 JSON 格式驗證。
