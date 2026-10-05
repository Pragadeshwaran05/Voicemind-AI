let currentConvId = null;
const urlParams = new URLSearchParams(window.location.search);
const idParam = urlParams.get('id');
if (idParam) currentConvId = parseInt(idParam);

const chatHistory = document.getElementById('chat-history');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');
const voiceBtn = document.getElementById('voice-btn');
const statusDiv = document.getElementById('status');

let recognition;
let isRecording = false;

if ('webkitSpeechRecognition' in window) {
    recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    
    recognition.onstart = function() {
        isRecording = true;
        voiceBtn.classList.replace('btn-outline-info', 'btn-danger');
        statusDiv.innerText = "Listening...";
    };
    
    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        chatInput.value = transcript;
        sendMessage('VOICE');
    };
    
    recognition.onerror = function(event) {
        statusDiv.innerText = "Error: " + event.error;
        resetVoiceBtn();
    };
    
    recognition.onend = function() {
        resetVoiceBtn();
    };
} else {
    voiceBtn.style.display = 'none';
}

function resetVoiceBtn() {
    isRecording = false;
    voiceBtn.classList.replace('btn-danger', 'btn-outline-info');
    if(statusDiv.innerText === "Listening...") statusDiv.innerText = "";
}

voiceBtn.addEventListener('click', () => {
    if (isRecording) {
        recognition.stop();
    } else {
        recognition.start();
    }
});

function appendMessage(role, content) {
    const div = document.createElement('div');
    div.className = `p-2 mb-2 rounded ${role === 'user' ? 'bg-primary text-white ms-auto' : 'bg-secondary text-white me-auto'}`;
    div.style.maxWidth = '75%';
    div.innerText = content;
    chatHistory.appendChild(div);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

async function sendMessage(inputType = 'TEXT') {
    const text = chatInput.value.trim();
    if (!text) return;
    
    appendMessage('user', text);
    chatInput.value = '';
    statusDiv.innerText = "Thinking...";
    sendBtn.disabled = true;
    
    try {
        const res = await fetch('/api/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ message: text, conversation_id: currentConvId, input_type: inputType })
        });
        const data = await res.json();
        if (data.success) {
            currentConvId = data.conversation_id;
            appendMessage('assistant', data.response);
            if (inputType === 'VOICE') speak(data.response);
        } else {
            appendMessage('assistant', "Error: " + data.error);
        }
    } catch (e) {
        appendMessage('assistant', "Network Error.");
    }
    
    statusDiv.innerText = "";
    sendBtn.disabled = false;
}

sendBtn.addEventListener('click', () => sendMessage('TEXT'));
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage('TEXT');
});

function speak(text) {
    if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(text);
        window.speechSynthesis.speak(utterance);
    }
}

// Load conversation if ID is set
if (currentConvId) {
    fetch('/api/conversations/' + currentConvId)
    .then(r => r.json())
    .then(data => {
        if(data.success) {
            data.messages.forEach(m => appendMessage(m.role, m.content));
        }
    });
}
