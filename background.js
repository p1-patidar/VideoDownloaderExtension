// Background script to handle messages from content scripts

const NATIVE_HOST_NAME = 'com.videodownloader.native';

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'downloadVideo') {
        downloadVideo(request.url)
            .then(response => sendResponse({ success: true, data: response }))
            .catch(error => sendResponse({ success: false, error: error.message }));
        return true; // Will respond asynchronously
    }

    if (request.action === 'startServer') {
        // Use native messaging to start the server
        chrome.runtime.sendNativeMessage(
            NATIVE_HOST_NAME,
            { action: 'start_server' },
            (response) => {
                if (chrome.runtime.lastError) {
                    sendResponse({ success: false, error: chrome.runtime.lastError.message });
                } else {
                    sendResponse({ success: true, data: response });
                }
            }
        );
        return true; // Will respond asynchronously
    }
});

async function downloadVideo(url) {
    try {
        const response = await fetch('http://127.0.0.1:8000/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url: url })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Unknown error from server');
        }

        return data;
    } catch (error) {
        console.error('Download error:', error);
        throw error;
    }
}
