# Deployment Guide: Making FinMentor AI Accessible

This guide explains how to make your locally running FinMentor AI system accessible to others, either on your local Wi-Fi network or over the internet.

## Option 1: Local Network (LAN) Access
**Best for:** Demos within the same room/Wi-Fi network.

### 1. Find your Local IP Address
*   **Windows**: Open Command Prompt (`cmd`) and run `ipconfig`. Look for "IPv4 Address" (e.g., `192.168.1.5`).
*   **Mac/Linux**: Run `ifconfig` or `ip a`.

### 2. Run the Backend
Instead of the default command, run the backend with `host="0.0.0.0"` to listen on all network interfaces.

```bash
# In the backend directory
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Run the Frontend
Update your frontend configuration (usually `.env` or `vite.config.js`) to point to your computer's IP address instead of `localhost`.

```bash
# In the frontend directory
npm run dev -- --host
```

### 4. Accessing from other devices
*   **Backend API**: `http://<YOUR_IP_ADDRESS>:8000`
*   **Frontend**: `http://<YOUR_IP_ADDRESS>:5173` (or whatever port Vite uses)

---

## Option 2: Internet Access (ngrok)
**Best for:** Demos to people outside your network or for testing webhooks.

### 1. Install ngrok
Download and install ngrok from [ngrok.com](https://ngrok.com/).

### 2. Start your Local Server
Run your backend normally:
```bash
uvicorn main:app --reload
```

### 3. Start ngrok Tunnel
Open a new terminal and run:
```bash
ngrok http 8000
```

### 4. Share the URL
ngrok will generate a public URL (e.g., `https://a1b2-c3d4.ngrok-free.app`).
*   Share this URL with others.
*   **Note**: You may need to update your Frontend's API base URL to use this new ngrok URL.

---

## Option 3: Cloud Deployment (Production)
For a permanent solution, deploy to a cloud provider.

### Backend (Render/Railway)
1.  Push code to GitHub.
2.  Connect repository to **Render** or **Railway**.
3.  Set Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4.  Add Environment Variables from your `.env` file.

### Frontend (Vercel/Netlify)
1.  Push code to GitHub.
2.  Connect repository to **Vercel** or **Netlify**.
3.  Update build settings (Command: `npm run build`, Output: `dist`).
4.  Set Environment Variable `VITE_API_URL` to your deployed Backend URL.
