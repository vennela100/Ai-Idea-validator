// Test script for voice assistant debugging
// Copy and paste this into the browser console when on the voice assistant page

function testVoiceAssistant() {
    console.log('=== Voice Assistant Test ===');
    
    // Test 1: Check if elements exist
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendButton');
    const chatMicButton = document.getElementById('chatMicButton');
    
    console.log('Elements found:', {
        messageInput: !!messageInput,
        sendButton: !!sendButton,
        chatMicButton: !!chatMicButton
    });
    
    // Test 2: Check voice settings
    console.log('Voice settings:', window.voiceSettings);
    
    // Test 3: Test a simple message
    if (messageInput && sendButton) {
        console.log('Testing simple message...');
        messageInput.value = 'test business idea';
        sendButton.disabled = false;
        
        // Manually trigger send
        const event = new Event('click');
        sendButton.dispatchEvent(event);
    }
    
    // Test 4: Test direct API call
    console.log('Testing direct API call...');
    fetch('/voice_assistant/voice-analyze/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            text: 'test business idea',
            language: 'en'
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Direct API response:', data);
    })
    .catch(error => {
        console.error('Direct API error:', error);
    });
    
    // Helper function to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
}

// Run the test
testVoiceAssistant();
