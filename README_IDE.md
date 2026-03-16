# AI Web IDE

This project has been upgraded to a full AI-powered Web IDE.

## Features
- **File Explorer**: Browse and manage files in your workspace.
- **Code Editor**: Monaco Editor (VS Code engine) with syntax highlighting.
- **Terminal**: Run scripts (Python, Node.js) and shell commands directly from the browser.
- **AI Assistant**: Integrated chat to ask questions, generate code, or explain files.
  - Supports OpenAI-compatible APIs (OpenAI, DeepSeek, Local LLMs).
  - Configure your API Key and Base URL in the Settings panel.

## How to Run

1. **Start the Backend**:
   ```bash
   python backend/main.py
   ```
   (The backend runs on http://localhost:8000)

2. **Open the Frontend**:
   Open `frontend/index.html` in your web browser.

## AI Configuration
Click the "Settings" icon in the AI Assistant panel to set your API Key.
- **Base URL**: Defaults to `https://api.openai.com/v1`. Change this for other providers (e.g., `http://localhost:1234/v1` for local LLMs).
- **Model**: Defaults to `gpt-3.5-turbo`. Change as needed.
