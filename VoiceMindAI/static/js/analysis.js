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
