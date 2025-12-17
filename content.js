// Content script to detect videos and inject download buttons

const DOWNLOAD_ICON = `
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
  <polyline points="7 10 12 15 17 10"></polyline>
  <line x1="12" y1="15" x2="12" y2="3"></line>
</svg>
`;

function createDownloadButton(videoUrl) {
    const btn = document.createElement('div');
    btn.className = 'vde-download-btn';
    btn.innerHTML = DOWNLOAD_ICON;
    btn.title = 'Download Video';

    // Style the button
    Object.assign(btn.style, {
        position: 'absolute',
        top: '10px',
        right: '10px',
        zIndex: '9999',
        backgroundColor: 'rgba(0, 0, 0, 0.7)',
        color: 'white',
        padding: '8px',
        borderRadius: '50%',
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        transition: 'background-color 0.2s',
        width: '40px',
        height: '40px'
    });

    btn.addEventListener('mouseenter', () => {
        btn.style.backgroundColor = 'rgba(0, 0, 0, 0.9)';
    });

    btn.addEventListener('mouseleave', () => {
        btn.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
    });

    btn.addEventListener('click', async (e) => {
        e.preventDefault();
        e.stopPropagation();

        // Visual feedback
        const originalContent = btn.innerHTML;
        btn.innerHTML = '<div class="vde-spinner"></div>'; // Simple spinner or just "..."
        btn.style.cursor = 'wait';

        // Use the current page URL as the video URL for yt-dlp to parse
        // This is often more reliable than the raw video source URL for sites like YouTube
        const targetUrl = window.location.href;

        chrome.runtime.sendMessage({
            action: 'downloadVideo',
            url: targetUrl
        }, (response) => {
            if (response && response.success) {
                btn.innerHTML = '✓';
                btn.style.backgroundColor = '#4CAF50';
                setTimeout(() => {
                    btn.innerHTML = originalContent;
                    btn.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
                    btn.style.cursor = 'pointer';
                }, 3000);
            } else {
                btn.innerHTML = '✗';
                btn.style.backgroundColor = '#f44336';
                alert('Download failed: ' + (response ? response.error : 'Unknown error'));
                setTimeout(() => {
                    btn.innerHTML = originalContent;
                    btn.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
                    btn.style.cursor = 'pointer';
                }, 3000);
            }
        });
    });

    return btn;
}

function processVideo(video) {
    // Check if we already processed this video
    if (video.dataset.vdeProcessed) return;

    // Ensure the video has a parent we can position relative to
    const parent = video.parentElement;
    if (!parent) return;

    // Make parent relative if it's static
    const parentStyle = window.getComputedStyle(parent);
    if (parentStyle.position === 'static') {
        parent.style.position = 'relative';
    }

    const btn = createDownloadButton();
    parent.appendChild(btn);

    video.dataset.vdeProcessed = 'true';
}

function initObserver() {
    // Process existing videos
    document.querySelectorAll('video').forEach(processVideo);

    // Observe for new videos
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            mutation.addedNodes.forEach((node) => {
                if (node.nodeType === 1) { // Element node
                    if (node.tagName === 'VIDEO') {
                        processVideo(node);
                    } else {
                        // Check children
                        node.querySelectorAll && node.querySelectorAll('video').forEach(processVideo);
                    }
                }
            });
        });
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
}

// Inject some basic CSS for the spinner
const style = document.createElement('style');
style.textContent = `
  .vde-spinner {
    border: 2px solid rgba(255,255,255,0.3);
    border-radius: 50%;
    border-top: 2px solid #fff;
    width: 16px;
    height: 16px;
    animation: vde-spin 1s linear infinite;
  }
  @keyframes vde-spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;
document.head.appendChild(style);

// Start
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initObserver);
} else {
    initObserver();
}
