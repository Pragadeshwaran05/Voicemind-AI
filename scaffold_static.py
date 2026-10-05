import os

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip() + '\n')
    print(f"Created {path}")

base = "VoiceMindAI"

write_file(f"{base}/static/css/style.css", """
body {
    background-color: #0b0f19;
    color: #e2e8f0;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

#wrapper {
    overflow-x: hidden;
}

#sidebar-wrapper {
    min-height: 100vh;
    margin-left: -15rem;
    transition: margin .25s ease-out;
    width: 15rem;
    background: linear-gradient(180deg, #111827 0%, #1f2937 100%) !important;
}

#sidebar-wrapper .list-group {
    width: 15rem;
}

#page-content-wrapper {
    min-width: 100vw;
}

#wrapper.toggled #sidebar-wrapper {
    margin-left: 0;
}

.glassmorphism {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.3);
}

.card {
    background-color: transparent;
    color: #fff;
}

textarea.glassmorphism, input.glassmorphism {
    background: rgba(0, 0, 0, 0.2);
    color: white;
}

textarea.glassmorphism:focus, input.glassmorphism:focus {
    background: rgba(0, 0, 0, 0.3);
    color: white;
}

@media (min-width: 768px) {
    #sidebar-wrapper {
        margin-left: 0;
    }
    #page-content-wrapper {
        min-width: 0;
        width: 100%;
    }
    #wrapper.toggled #sidebar-wrapper {
        margin-left: -15rem;
    }
}
""")

write_file(f"{base}/static/js/main.js", """
document.getElementById('menu-toggle').addEventListener('click', function(e) {
    e.preventDefault();
    document.getElementById('wrapper').classList.toggle('toggled');
});
""")

write_file(f"{base}/static/js/chat.js", """
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
""")

write_file(f"{base}/static/js/analysis.js", """
const btn = document.getElementById('analyze-btn');
const input = document.getElementById('analysis-text');
const loading = document.getElementById('analysis-loading');
const results = document.getElementById('analysis-results');

btn.addEventListener('click', async () => {
    const text = input.value.trim();
    if (!text) return alert("Please enter text");
    
    btn.disabled = true;
    loading.style.display = 'block';
    results.style.display = 'none';
    
    try {
        const res = await fetch('/api/analyze', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ text: text })
        });
        const data = await res.json();
        
        if (data.success) {
            document.getElementById('res-sentiment').innerText = data.sentiment || 'N/A';
            document.getElementById('res-intent').innerText = data.intent || 'N/A';
            document.getElementById('res-emotion').innerText = data.emotion || 'N/A';
            document.getElementById('res-words').innerText = data.word_count || 0;
            document.getElementById('res-keywords').innerText = (data.keywords || []).join(', ');
            document.getElementById('res-topics').innerText = (data.topics || []).join(', ');
            results.style.display = 'flex';
        } else {
            alert(data.error);
        }
    } catch (e) {
        alert("Error connecting to server.");
    }
    
    btn.disabled = false;
    loading.style.display = 'none';
});
""")

write_file(f"{base}/static/js/summarizer.js", """
const btn = document.getElementById('summarize-btn');
const input = document.getElementById('sum-text');
const fileInput = document.getElementById('sum-file');
const loading = document.getElementById('sum-loading');
const results = document.getElementById('sum-results');

btn.addEventListener('click', async () => {
    if (!input.value.trim() && !fileInput.files.length) {
        return alert("Please enter text or upload a file.");
    }
    
    btn.disabled = true;
    loading.style.display = 'block';
    results.style.display = 'none';
    
    const formData = new FormData();
    if (fileInput.files.length > 0) {
        formData.append('file', fileInput.files[0]);
    } else {
        formData.append('text', input.value.trim()); // Fallback text but backend JSON preferred for text
    }
    
    try {
        let options = { method: 'POST' };
        if (fileInput.files.length > 0) {
            options.body = formData;
        } else {
            options.headers = {'Content-Type': 'application/json'};
            options.body = JSON.stringify({text: input.value.trim()});
        }
        
        const res = await fetch('/api/summarize', options);
        const data = await res.json();
        
        if (data.success) {
            document.getElementById('res-summary').innerText = data.summary;
            document.getElementById('res-points').innerHTML = (data.key_points || []).map(p => `<li>${p}</li>`).join('');
            document.getElementById('res-actions').innerHTML = (data.action_items || []).map(p => `<li>${p}</li>`).join('');
            results.style.display = 'flex';
        } else {
            alert(data.error);
        }
    } catch (e) {
        alert("Error connecting to server.");
    }
    
    btn.disabled = false;
    loading.style.display = 'none';
});
""")
