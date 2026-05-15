# Deployment Guide

Stack:

- **Frontend** — Vite + React, deployed to **Vercel**
- **Backend** — Flask + Gunicorn, deployed to **Render.com** (free tier)
- **Model** — `q_table_clean.json` is committed at the repo root, served directly by the backend

Total time end-to-end: ~15 minutes the first time.

---

## 1. Deploy the backend to Render

1. Go to <https://dashboard.render.com> and sign in with GitHub.
2. **New +** → **Blueprint**.
3. Connect this repository (`xircons/tictactoe-qlearning`). Render reads
   `deployment/render.yaml` automatically and proposes a web service named
   `tictactoe-ai-api`. Click **Apply**.
4. Wait for the first deploy (~2 min build + ~30s startup).
5. Copy the service URL — looks like `https://tictactoe-ai-api.onrender.com`.
   You'll need it in step 2.
6. Verify it works:
   ```bash
   curl https://tictactoe-ai-api.onrender.com/api/health
   ```
   Should return JSON with `"q_table_loaded": true` and `"q_states": 4520`.

### Free-tier caveats

- The instance **sleeps after 15 minutes of inactivity** and takes ~30 seconds
  to wake up on the next request. The frontend should show a loading state
  during that cold start.
- 750 free hours/month per workspace.
- If you need always-on, upgrade to a paid plan ($7/mo) or pair with a free
  uptime pinger like UptimeRobot.

### CORS

The backend already allows `https://*.vercel.app`. If you attach a custom
domain to the Vercel deployment, set this env var in Render dashboard:

```
ALLOWED_ORIGINS=https://your-custom-domain.com,https://www.your-custom-domain.com
```

---

## 2. Deploy the frontend to Vercel

1. Go to <https://vercel.com/new>.
2. **Import** the same GitHub repo.
3. Vercel auto-detects Vite. Configure:
   - **Root Directory**: `frontend`
   - **Framework Preset**: Vite (auto)
   - **Build Command**: `npm run build` (auto)
   - **Output Directory**: `dist` (auto)
4. **Environment Variables** — add one:
   - Name: `VITE_API_PRODUCTION_URL`
   - Value: `https://tictactoe-ai-api.onrender.com` (the URL from step 1.5)
   - Environment: Production, Preview, Development
5. **Deploy**.
6. Once it's live, open the Vercel URL and try a game.

### What Vercel handles for you

- HTTPS + custom domains
- Preview deployments on every PR
- SPA routing via `frontend/vercel.json` (rewrites all paths to `index.html`)

### Re-deploy after API URL change

If you ever swap the backend URL, update `VITE_API_PRODUCTION_URL` in Vercel
project settings, then click **Redeploy** on the latest deployment.

---

## 3. Local development

Backend:

```bash
cd ~/Documents/GitHub/tictactoe-ai
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 backend/main.py
# → http://localhost:5001
```

Frontend:

```bash
cd frontend
npm install
cp .env.example .env.local   # first time only
npm run dev
# → http://localhost:3000
```

The frontend's `api.js` auto-detects dev mode and hits `localhost:5001`. Make
sure `VITE_API_LOCAL_URL` in `.env.local` points to your local backend if you
override the default.

---

## 4. Re-training the model

The committed `q_table_clean.json` is the 500k-episode Clean Q-learner. To
retrain:

```bash
source .venv/bin/activate
python3 src/training/train_clean.py 500000
git add q_table_clean.json
git commit -m "retrain: q_table_clean 500k"
git push
```

Render will auto-deploy on push to `main`. (~3 minutes until backend serves
the new model.)

---

## 5. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Frontend shows "Failed to fetch" | Backend cold-starting, or wrong URL | Wait 30 s; verify `VITE_API_PRODUCTION_URL` in Vercel; hit `/api/health` directly |
| AI plays random moves | `q_table_loaded: false` in `/api/health` | Q-table not committed or in unexpected path. Set `Q_TABLE_PATH` env var on Render. |
| CORS error in browser console | Vercel domain not allowed | Set `ALLOWED_ORIGINS` env var on Render to include your Vercel URL |
| 404 on direct route navigation (e.g. `/game`) | SPA rewrite missing | Verify `frontend/vercel.json` is committed |
| Build fails on Render with `ModuleNotFoundError` | Dependency missing | Add to `requirements.txt`, push |
| Slow first request after idle | Free-tier sleep | Expected — upgrade plan or use UptimeRobot |
