const downloadBtn = document.getElementById('downloadBtn');
const statusEl = document.getElementById('status');

function setStatus(message, isError = false) {
  statusEl.textContent = message;
  statusEl.style.color = isError ? 'crimson' : 'inherit';
}

downloadBtn.addEventListener('click', async () => {
  setStatus('正在取得當前分頁網址...');

  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    const url = tab && tab.url;

    if (!url || !/^https?:\/\//i.test(url)) {
      setStatus('目前分頁不是可下載的網頁網址。', true);
      return;
    }

    const response = await chrome.runtime.sendMessage({
      type: 'DOWNLOAD_CURRENT_VIDEO',
      url
    });

    if (!response || !response.ok) {
      setStatus(response?.error || '下載請求失敗。', true);
      return;
    }

    setStatus('已送出下載命令，請查看本機 Downloads 資料夾。');
  } catch (error) {
    setStatus(`發生錯誤：${error.message}`, true);
  }
});
