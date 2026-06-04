@echo off
setlocal

set "HOST_NAME=com.ytdlp.downloader"
set "MANIFEST_PATH=%~dp0host_manifest.json"

for %%I in ("%MANIFEST_PATH%") do set "MANIFEST_PATH=%%~fI"

reg add "HKCU\Software\Google\Chrome\NativeMessagingHosts\%HOST_NAME%" /ve /t REG_SZ /d "%MANIFEST_PATH%" /f

if errorlevel 1 (
  echo [ERROR] 註冊失敗，請以一般使用者身分確認可寫入 HKCU。
  exit /b 1
)

echo [OK] 已註冊 Native Messaging Host:
echo %HOST_NAME%
echo %MANIFEST_PATH%

echo.
echo 請確認 host_manifest.json 中的 path 與 allowed_origins 已正確填寫。
endlocal
