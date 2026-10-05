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
