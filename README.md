# 🧠 AI-Powered Technical Interviewer

Welcome to the **AI-Powered Technical Interviewer**, a state-of-the-art full-stack platform designed to help developers sharpen their technical skills. The application simulates real-world backend, frontend, devops, and full-stack technical interviews, allowing candidates to write code and answer questions verbally. It provides instant, multi-dimensional feedback powered by local AI intelligence.

Developed and maintained by **Tanushri Sukhwal**.

---

## ✨ Features

- **Dynamic Question Generation**: Instantly generates role-specific (e.g., MERN Stack, Python, DevOps) and level-specific (Junior, Mid, Senior) questions using localized LLMs.
- **Hybrid Input System**:
  - **🎙️ Voice Responses**: Captures candidate voice answers, transcribes them locally via **OpenAI Whisper**, and evaluates their verbal confidence and technical understanding.
  - **💻 Monaco Code Editor**: Real-time syntax-highlighted code editor for solving coding questions directly in the browser.
- **AI-Powered Grading & Feedback**:
  - Scores submissions from `0` to `100` on both **Technical Accuracy** and **Verbal Confidence**.
  - Highlights performance metrics and supplies an **Ideal Implementation/Explanation** for comparison.
- **Session History & Analytics**:
  - Track interview duration, overall performance averages, and per-question score distributions with charts powered by **Chart.js**.
- **Interactive Custom Modals**: Replaces native browser alerts with custom glassmorphic modals for premium aesthetics and sandboxed compatibility.

---

## 🛠️ Tech Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Frontend** | React (Vite), Redux Toolkit, TailwindCSS, Monaco Editor, Chart.js | Responsive candidate UI with charts and editors |
| **API Gateway** | Node.js, Express.js, MongoDB (Mongoose), Socket.io, JWT | Orchestrates interview sessions and handles state |
| **AI Service** | FastAPI, Uvicorn, Python, OpenAI Whisper | Local transcription and AI evaluation service |
| **LLM Engine** | Ollama (`deepseek-r1:1.5b`) | Low-latency local reasoning model |

---

## 🚀 Services Architecture & Setup

The application runs as three decoupled services. Make sure you have **Node.js**, **Python 3.9+**, and **Ollama** installed on your system.

### 1. Database & Secrets Setup
Create a `.env` file in the `backend/` directory:
```env
PORT=5001
MONGO_URI=your_mongodb_atlas_connection_string
JWT_SECRET=your_jwt_signing_key
NODE_ENV=development
```

### 2. Launching the API Gateway (Backend)
Navigate to the `backend/` folder, install dependencies, and start the development server:
```bash
cd backend
npm install
npm run dev
```
*The server will run on port `5001`.*

### 3. Launching the Candidate UI (Frontend)
Create a `.env` file in the `frontend/` directory:
```env
VITE_API_URL=http://localhost:5001/api
```
Install dependencies and run the development server:
```bash
cd frontend
npm install
npm run dev
```
*The web app will run on port `5173` (or the next available port).*

### 4. Setting up the Local AI Engine (Ollama)
Install Ollama, start the server, and download the high-performance local reasoning model:
```bash
ollama serve
ollama pull deepseek-r1:1.5b
```

### 5. Launching the AI Microservice
Create a `.env` file in the `ai-service/` directory:
```env
AI_SERVICE_PORT=8000
OLLAMA_MODEL_NAME=deepseek-r1:1.5b
```
Navigate to the `ai-service/` folder, initialize a virtual environment, install dependencies, and start FastAPI:
```bash
cd ai-service
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn ollama openai-whisper pydub python-dotenv
python main.py
```
*The microservice will run on port `8000`.*

---

## 🙋‍♀️ About the Developer

This platform was built and refined by **Tanushri Sukhwal** to create a highly responsive, aesthetic, and fully local AI interview simulator. It leverages container-friendly AI microservices, clean state management, and modern glassmorphism design.

For inquiries or contributions, check out the GitHub repository: [AI-Interviewer on GitHub](https://github.com/TanushriS/AI-Interviewer).