# Skill Manager Dashboard

A simple fullstack application to list and run Python "skills" from a local directory.

## Project Structure
-   `backend/`: FastAPI server.
-   `frontend/`: HTML/JS/CSS dashboard.
-   `skills/`: Place your Python scripts here.

## How to Run

### 1. Setup Backend
Navigate to the `backend/` folder, install dependencies, and start the server:
```bash
cd backend
pip install -r requirements.txt
python main.py
```
The server will run at `http://localhost:8000`.

### 2. Run Frontend
Open `frontend/index.html` in your web browser.

## Features
-   **Dynamic Skill Loading**: Any `.py` file added to the `skills/` folder will automatically appear in the dashboard.
-   **Execution**: Clicking "Run" executes the script via a subprocess and captures the output.
-   **Real-time Output**: Displays both `stdout` and `stderr` in the UI.
