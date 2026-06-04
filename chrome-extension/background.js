const HOST_NAME = 'com.ytdlp.downloader';

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message?.type !== 'DOWNLOAD_CURRENT_VIDEO') {
    return;
  }

  chrome.runtime.sendNativeMessage(
    HOST_NAME,
    { url: message.url },
    (nativeResponse) => {
      if (chrome.runtime.lastError) {
        sendResponse({ ok: false, error: chrome.runtime.lastError.message });
        return;
      }

      if (!nativeResponse || nativeResponse.ok !== true) {
        sendResponse({ ok: false, error: nativeResponse?.error || 'Native host 回應異常。' });
        return;
      }

      sendResponse({ ok: true, message: nativeResponse.message });
    }
  );

  return true;
});
