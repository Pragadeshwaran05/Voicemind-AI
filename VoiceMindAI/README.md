# VoiceMind AI

**Speak. Think. Understand.**

VoiceMind AI is a full-stack Flask web application that seamlessly blends text and speech input. You can converse, analyze, and summarize your data all in one intelligent interface.

## 🚀 Features Completed

1. **Dashboard:** Live SQLite statistics for messages, conversations, and interaction types (Text vs Voice).
2. **AI Chat & Voice Assistant:** 
   - Talk to the AI using your microphone (powered by Web Speech API).
   - Get responses read out to you via text-to-speech.
   - Text chat with full Gemini integration.
   - Saves conversations to the SQLite database.
3. **Text & Speech Analysis:** Real-time sentiment, intent, emotion, keyword extraction, and topic modeling.
4. **Smart Summarizer:** Paste text or upload a `.txt` file to receive structured summaries and key action items.

## 🛠️ Technology Stack

- **Frontend:** HTML5, CSS3, JavaScript (Bootstrap 5 for layout, Web Speech API for voice interactions)
- **Backend:** Python, Flask, SQLAlchemy
- **Database:** SQLite
- **AI Integration:** Google Generative AI (Gemini)

## 📂 Project Structure

```text
VoiceMindAI/
├── .env
├── .env.example
├── app.py
├── config.py
├── requirements.txt
├── instance/
│   └── voicemind.db
├── models/
│   └── __init__.py
├── routes/
│   ├── analysis.py
│   ├── chat.py
│   ├── main.py
│   └── summarizer.py
├── services/
│   └── ai_service.py
├── static/
│   ├── css/style.css
│   └── js/
│       ├── analysis.js
│       ├── chat.js
│       ├── main.js
│       └── summarizer.js
└── templates/
    ├── analysis.html
    ├── base.html
    ├── chat.html
    ├── dashboard.html
    └── summarizer.html
```

## ⚙️ Installation & Running

The files have been generated at `c:\Users\Pragadesh\OneDrive\Desktop\VOICEMIND AI\VoiceMindAI`.

**Step 1: Configure Environment Variables**
Open `VoiceMindAI/.env` and replace `YOUR_API_KEY` with your actual Gemini API key.

```env
SECRET_KEY=dev_secret_key_12345
AI_API_KEY=your_real_gemini_api_key_here
AI_MODEL=gemini-1.5-flash
DATABASE_URL=sqlite:///voicemind.db
```

**Step 2: Activate the Virtual Environment**
If you open a new terminal:
```bash
cd "C:\Users\Pragadesh\OneDrive\Desktop\VOICEMIND AI\VoiceMindAI"
venv\Scripts\activate
```

**Step 3: Run the Application**
```bash
python app.py
```
Open `http://localhost:5000` in a browser. 

*Note: Voice features require microphone permissions in the browser.*
