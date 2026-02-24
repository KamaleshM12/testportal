# Frontend (Vite + React)

Run locally:

```powershell
cd frontend
npm install
npm run dev
```

This starts a dev server (default http://localhost:5173). The app calls the backend at `http://127.0.0.1:8000/execute` — ensure the FastAPI server is running and CORS is enabled (already configured for `localhost:5173`).
