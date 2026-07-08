# 🚀 Deployment Guide: AI-Powered Technical Interviewer

This guide details how to deploy the entire application to production. Since the application is split into three decoupled services, we will use a hybrid deployment architecture:
1. **Frontend (React)**: Deployed on **Vercel**.
2. **Backend (Node.js + Socket.io)**: Deployed on a persistent host (e.g., **Render** or **Railway**).
3. **AI Service (FastAPI + Ollama)**: Deployed as a container on a persistent host (e.g., **Railway** or **Render**).

---

## 🎨 1. Frontend Deployment (Vercel)

The React client is built with Vite. We have created a `vercel.json` configuration to handle Single Page Application (SPA) routing to prevent `404` errors when reloading dashboards or interview runner pages.

### Steps to Deploy on Vercel:
1. Go to [Vercel](https://vercel.com/) and create a new project.
2. Link your GitHub repository.
3. In the project settings:
   - **Framework Preset**: `Vite` (or `Other` if Vite is detected automatically)
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. Add the following **Environment Variable**:
   - `VITE_API_URL`: `https://your-backend-service-url.com/api` (Point this to your production backend URL, which you will get in Step 2).
5. Click **Deploy**.

---

## 🔌 2. Backend Deployment (Render / Railway)

The backend server relies on **Socket.io (WebSockets)**, which is **not** supported by serverless platforms like Vercel. You must deploy it on a persistent platform (e.g., a Render Web Service or a Railway Service).

### Steps to Deploy on Render:
1. Create a new **Web Service** on Render.
2. Connect your GitHub repository.
3. Configure the settings:
   - **Root Directory**: `backend`
   - **Runtime**: `Node`
   - **Build Command**: `npm install`
   - **Start Command**: `npm start`
4. Add the following **Environment Variables**:
   - `PORT`: `5001` (Render will automatically bind it, but define it just in case)
   - `MONGO_URI`: `your_mongodb_atlas_connection_string`
   - `JWT_SECRET`: `your_secure_jwt_signing_key`
   - `NODE_ENV`: `production`
5. Click **Deploy**. Note the URL (e.g., `https://your-backend.onrender.com`). Use this URL (with `/api` appended) to set `VITE_API_URL` in your Vercel frontend.

---

## 🧠 3. AI Service Deployment (Railway / Render Container)

The AI service runs FastAPI, OpenAI Whisper, and local Ollama (`deepseek-r1:1.5b` + `nomic-embed-text:latest`). Because it requires local model binaries, we packaged it into a `Dockerfile`.

### Steps to Deploy:
1. We have provided `ai-service/Dockerfile` and `ai-service/start.sh` which automatically installs Ollama and pulls the DeepSeek-R1 and Nomic Embed models during the container boot sequence.
2. Deploy this container on **Railway** or **Render** as a **Docker Service** (source directory: `ai-service`).
3. **Instance Requirements**:
   - The instance must have at least **2GB RAM** (4GB recommended) to comfortably load and run the `1.1GB` DeepSeek model and run Whisper audio transcribing.
4. Add the following **Environment Variables**:
   - `PORT`: `8000`
   - `AI_SERVICE_PORT`: `8000`
   - `OLLAMA_MODEL_NAME`: `deepseek-r1:1.5b`
5. Click **Deploy**.

---

## 💡 Production alternative: Refactoring to Serverless (Cloud APIs)

If you wish to deploy the entire project (including the AI components) purely on Vercel serverless functions without the need for expensive persistent container hosting, you can refactor the services to use cloud APIs instead of local binaries:
1. **Replace Local Ollama with Gemini API**: 
   - Integrate the **Google Gemini API** directly via the `@google/genai` or `google-genai` Python library. It has a generous free tier, near-zero latency, and does not require running a heavy local server.
2. **Replace Local Whisper with OpenAI Whisper API / Cloud STT**:
   - Post audio files to the hosted Whisper API rather than importing the 140MB local Python model.
3. This will make the AI Service extremely lightweight, enabling you to merge the FastAPI serverless functions directly into Vercel or run them in standard, cheap serverless runtimes.
