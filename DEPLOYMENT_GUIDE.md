# Deployment Guide (Vercel + Render)

This project is set up for free hosting with:

- Frontend: Vercel (Next.js)
- Backend: Render (FastAPI)

## 1) Push to GitHub

From the repository root:

```bash
git init
git add .
git commit -m "deploy setup"
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main
```

## 2) Deploy Backend on Render

1. Go to Render dashboard and choose **New +** -> **Blueprint**.
2. Connect your GitHub repo.
3. Render will detect `render.yaml` and create the backend service.
4. Wait for deploy to finish.
5. Open the service URL and verify:

```bash
https://<your-render-url>/health
```

You should see:

```json
{"status":"ok"}
```

## 3) Deploy Frontend on Vercel

1. Go to Vercel dashboard and **Add New Project**.
2. Import the same GitHub repo.
3. Set **Root Directory** to `frontend`.
4. Add environment variable:

- `NEXT_PUBLIC_API_BASE_URL` = `https://<your-render-url>`

5. Deploy.

## 4) Verify End-to-End

1. Open Vercel URL.
2. Run a backtest from the dashboard.
3. Confirm charts and metrics load from live backend.

## Notes for Free Tier

- Render free instances may sleep when idle.
- First request after idle can be slow.
- If frontend loads before backend wakes up, retry the request once.
- Backend cache uses lightweight JSON files, so no native parquet wheels are required on the host.
