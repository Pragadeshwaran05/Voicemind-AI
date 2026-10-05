import os

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip() + '\n')
    print(f"Created {path}")

base = "VoiceMindAI"

write_file(f"{base}/templates/base.html", """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VoiceMind AI</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <div class="d-flex" id="wrapper">
        <!-- Sidebar -->
        <div class="bg-dark border-right text-light" id="sidebar-wrapper">
            <div class="sidebar-heading fs-4 fw-bold p-3">🧠 VoiceMind AI</div>
            <div class="list-group list-group-flush">
                <a href="/" class="list-group-item list-group-item-action bg-dark text-light"><i class="fa fa-home"></i> Dashboard</a>
                <a href="/chat" class="list-group-item list-group-item-action bg-dark text-light"><i class="fa fa-comments"></i> AI Chat</a>
                <a href="/chat" class="list-group-item list-group-item-action bg-dark text-light"><i class="fa fa-microphone"></i> Voice Assistant</a>
                <a href="/analysis" class="list-group-item list-group-item-action bg-dark text-light"><i class="fa fa-chart-bar"></i> Text & Speech Analysis</a>
                <a href="/summarizer" class="list-group-item list-group-item-action bg-dark text-light"><i class="fa fa-file-alt"></i> Smart Summarizer</a>
            </div>
        </div>
        <!-- /#sidebar-wrapper -->

        <!-- Page Content -->
        <div id="page-content-wrapper" class="w-100">
            <nav class="navbar navbar-expand-lg navbar-dark bg-dark border-bottom">
                <button class="btn btn-outline-light ms-2" id="menu-toggle"><i class="fa fa-bars"></i></button>
            </nav>

            <div class="container-fluid p-4">
                {% block content %}{% endblock %}
            </div>
        </div>
        <!-- /#page-content-wrapper -->
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
    {% block scripts %}{% endblock %}
</body>
</html>
""")

write_file(f"{base}/templates/dashboard.html", """
{% extends 'base.html' %}
{% block content %}
<div class="row">
    <div class="col-12 text-center mb-5">
        <h1 class="display-4">Welcome to VoiceMind AI</h1>
        <p class="lead">Speak naturally or type your question.</p>
    </div>
</div>

<div class="row text-center mb-5">
    <div class="col-md-3">
        <div class="card glassmorphism p-3">
            <h3>{{ total_convs }}</h3>
            <p>Total Conversations</p>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card glassmorphism p-3">
            <h3>{{ total_msgs }}</h3>
            <p>Total Messages</p>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card glassmorphism p-3">
            <h3>{{ voice_msgs }}</h3>
            <p>Voice Interactions</p>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card glassmorphism p-3">
            <h3>{{ text_msgs }}</h3>
            <p>Text Interactions</p>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-md-12">
        <h3>Recent Conversations</h3>
        <ul class="list-group glassmorphism">
            {% for conv in recent_convs %}
            <li class="list-group-item bg-transparent text-light border-secondary">
                <a href="/chat?id={{ conv.id }}" class="text-info text-decoration-none">{{ conv.title }}</a> 
                <small class="float-end">{{ conv.created_at.strftime('%Y-%m-%d %H:%M') }}</small>
            </li>
            {% else %}
            <li class="list-group-item bg-transparent text-light border-secondary">No recent conversations.</li>
            {% endfor %}
        </ul>
    </div>
</div>
{% endblock %}
""")

write_file(f"{base}/templates/chat.html", """
{% extends 'base.html' %}
{% block content %}
<div class="row h-100">
    <div class="col-md-12 d-flex flex-column h-100" style="max-height: 80vh;">
        <div id="chat-history" class="flex-grow-1 overflow-auto p-3 mb-3 border rounded glassmorphism">
            <!-- Messages go here -->
        </div>
        <div class="d-flex align-items-center">
            <button id="voice-btn" class="btn btn-outline-info me-2 rounded-circle" style="width:50px; height:50px;"><i class="fa fa-microphone"></i></button>
            <input type="text" id="chat-input" class="form-control me-2" placeholder="Type or speak a message..." aria-label="Message">
            <button id="send-btn" class="btn btn-primary">Send</button>
        </div>
        <div id="status" class="text-muted mt-2 small"></div>
    </div>
</div>
{% endblock %}
{% block scripts %}
<script src="{{ url_for('static', filename='js/chat.js') }}"></script>
{% endblock %}
""")

write_file(f"{base}/templates/analysis.html", """
{% extends 'base.html' %}
{% block content %}
<h2>Text & Speech Analysis</h2>
<div class="row mt-4">
    <div class="col-md-12">
        <textarea id="analysis-text" class="form-control mb-3 glassmorphism text-light" rows="5" placeholder="Enter text to analyze..."></textarea>
        <button id="analyze-btn" class="btn btn-primary">Analyze</button>
        <div id="analysis-loading" class="mt-2 text-info" style="display:none;">Analyzing...</div>
    </div>
</div>
<div class="row mt-4" id="analysis-results" style="display:none;">
    <div class="col-md-3"><div class="card glassmorphism p-3"><h5>Sentiment</h5><p id="res-sentiment"></p></div></div>
    <div class="col-md-3"><div class="card glassmorphism p-3"><h5>Intent</h5><p id="res-intent"></p></div></div>
    <div class="col-md-3"><div class="card glassmorphism p-3"><h5>Emotion</h5><p id="res-emotion"></p></div></div>
    <div class="col-md-3"><div class="card glassmorphism p-3"><h5>Word Count</h5><p id="res-words"></p></div></div>
    <div class="col-md-6 mt-3"><div class="card glassmorphism p-3"><h5>Keywords</h5><p id="res-keywords"></p></div></div>
    <div class="col-md-6 mt-3"><div class="card glassmorphism p-3"><h5>Topics</h5><p id="res-topics"></p></div></div>
</div>
{% endblock %}
{% block scripts %}
<script src="{{ url_for('static', filename='js/analysis.js') }}"></script>
{% endblock %}
""")

write_file(f"{base}/templates/summarizer.html", """
{% extends 'base.html' %}
{% block content %}
<h2>Smart Summarizer</h2>
<div class="row mt-4">
    <div class="col-md-12">
        <textarea id="sum-text" class="form-control mb-3 glassmorphism text-light" rows="6" placeholder="Paste content here to summarize..."></textarea>
        <input type="file" id="sum-file" class="form-control mb-3 glassmorphism text-light" accept=".txt">
        <button id="summarize-btn" class="btn btn-primary">Summarize</button>
        <div id="sum-loading" class="mt-2 text-info" style="display:none;">Summarizing...</div>
    </div>
</div>
<div class="row mt-4" id="sum-results" style="display:none;">
    <div class="col-md-12">
        <div class="card glassmorphism p-3 mb-3">
            <h5>Summary</h5>
            <p id="res-summary"></p>
        </div>
        <div class="card glassmorphism p-3 mb-3">
            <h5>Key Points</h5>
            <ul id="res-points"></ul>
        </div>
        <div class="card glassmorphism p-3 mb-3">
            <h5>Action Items</h5>
            <ul id="res-actions"></ul>
        </div>
    </div>
</div>
{% endblock %}
{% block scripts %}
<script src="{{ url_for('static', filename='js/summarizer.js') }}"></script>
{% endblock %}
""")
