document.addEventListener('DOMContentLoaded', function () {
  const downloadBtn = document.getElementById('downloadBtn');
  const statusDiv = document.getElementById('status');
  const urlInput = document.getElementById('videoUrl');
  const serverStatus = document.getElementById('serverStatus');
  const progressSection = document.getElementById('progressSection');
  const progressFill = document.getElementById('progressFill');
  const progressPercent = document.getElementById('progressPercent');
  const progressFilename = document.getElementById('progressFilename');
  const progressSize = document.getElementById('progressSize');
  const progressSpeed = document.getElementById('progressSpeed');
  const progressEta = document.getElementById('progressEta');

  let ws = null;
  const SERVER_URL = 'http://127.0.0.1:8000';
  const WS_URL = 'ws://127.0.0.1:8000/ws';

  // Path to open folder script (runs via Spotlight to open Finder)
  const OPEN_FOLDER_PATH = '/Users/pp/Desktop/VideoDownloaderExtension/open_folder.command';

  // Auto-fill URL from active tab
  chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
    if (tabs[0] && tabs[0].url) {
      urlInput.value = tabs[0].url;
    }
  });

  // Check server status on load
  checkServerStatus();

  // Server status click handler
  serverStatus.addEventListener('click', async () => {
    const isOnline = serverStatus.classList.contains('online');

    if (isOnline) {
      // Server running - ask backend to open Finder
      try {
        await fetch(`${SERVER_URL}/open-folder`);
      } catch (e) {
        console.error('Failed to open folder:', e);
      }
    } else {
      // Server not running - copy path and show instructions
      await navigator.clipboard.writeText(OPEN_FOLDER_PATH);
      const statusText = serverStatus.querySelector('.status-text');
      statusText.textContent = '✓ Copied!';
      setTimeout(() => {
        statusText.textContent = 'Start Server ▸';
      }, 2000);

      statusDiv.innerHTML = '📋 Path copied!<br><small><b>Cmd+Space</b> → paste → Enter → Opens Finder!</small>';
      statusDiv.className = 'info';
    }
  });

  async function checkServerStatus() {
    try {
      const response = await fetch(`${SERVER_URL}/health`, {
        method: 'GET',
        signal: AbortSignal.timeout(2000)
      });
      if (response.ok) {
        setServerOnline(true);
      } else {
        setServerOnline(false);
      }
    } catch (e) {
      setServerOnline(false);
    }
  }

  function setServerOnline(online) {
    const statusText = serverStatus.querySelector('.status-text');
    if (online) {
      serverStatus.classList.add('online');
      serverStatus.classList.remove('offline');
      statusText.textContent = 'Online';
      downloadBtn.disabled = false;
    } else {
      serverStatus.classList.add('offline');
      serverStatus.classList.remove('online');
      statusText.textContent = 'Start Server ▸';
      downloadBtn.disabled = false; // Still allow click to show error
    }
  }

  function connectWebSocket() {
    return new Promise((resolve, reject) => {
      ws = new WebSocket(WS_URL);

      ws.onopen = () => {
        console.log('WebSocket connected');
        resolve(ws);
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        reject(new Error('Could not connect to server. Please start the server first.'));
      };

      ws.onclose = () => {
        console.log('WebSocket closed');
        ws = null;
      };

      ws.onmessage = (event) => {
        handleMessage(JSON.parse(event.data));
      };
    });
  }

  function handleMessage(data) {
    switch (data.type) {
      case 'status':
        showProgress();
        progressFilename.textContent = data.message;
        break;

      case 'progress':
        showProgress();
        progressFill.style.width = `${data.percent}%`;
        progressPercent.textContent = `${data.percent}%`;
        progressFilename.textContent = data.filename || 'Downloading...';
        progressSize.textContent = `${data.downloaded} / ${data.total}`;
        progressSpeed.textContent = data.speed;
        progressEta.textContent = `ETA: ${data.eta}`;
        break;

      case 'processing':
        progressFill.style.width = '100%';
        progressPercent.textContent = '100%';
        progressFilename.innerHTML = '<span class="spinner"></span>' + data.message;
        progressSpeed.textContent = 'Merging...';
        progressEta.textContent = '';
        break;

      case 'complete':
        hideProgress();
        statusDiv.textContent = '✓ ' + data.message;
        statusDiv.className = 'success';
        downloadBtn.disabled = false;
        closeWebSocket();
        break;

      case 'error':
        hideProgress();
        statusDiv.textContent = '✗ ' + data.message;
        statusDiv.className = 'error';
        downloadBtn.disabled = false;
        closeWebSocket();
        break;
    }
  }

  function showProgress() {
    progressSection.classList.remove('hidden');
    statusDiv.textContent = '';
    statusDiv.className = '';
  }

  function hideProgress() {
    progressSection.classList.add('hidden');
    progressFill.style.width = '0%';
    progressPercent.textContent = '0%';
  }

  function closeWebSocket() {
    if (ws) {
      ws.close();
      ws = null;
    }
  }

  downloadBtn.addEventListener('click', async function () {
    const url = urlInput.value;
    if (!url) {
      statusDiv.textContent = 'Please enter a URL';
      statusDiv.className = 'error';
      return;
    }

    // Reset UI
    hideProgress();
    statusDiv.textContent = '';
    statusDiv.className = '';
    downloadBtn.disabled = true;

    try {
      // First check if server is online
      await checkServerStatus();

      // Connect via WebSocket
      await connectWebSocket();

      // Send download request
      ws.send(JSON.stringify({
        action: 'download',
        url: url
      }));

    } catch (error) {
      statusDiv.innerHTML = `Connection Error: ${error.message}<br><br><small>Click the status indicator above to copy server path.</small>`;
      statusDiv.className = 'error';
      downloadBtn.disabled = false;
    }
  });

  // Periodically check server status
  setInterval(checkServerStatus, 5000);
});
