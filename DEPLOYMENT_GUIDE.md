# Deployment Guide (Vercel + Hugging Face Spaces)

This project is set up for free hosting with:

- Frontend: Vercel (Next.js)
- Backend: Hugging Face Spaces (Docker)

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

## 2) Deploy Backend on Hugging Face Spaces

1. Go to Hugging Face and create a **New Space**.
2. Choose **Docker** as the SDK.
3. Connect the same GitHub repo.
4. Ensure the repository root contains the top-level `Dockerfile`.
5. Create the Space and let it build.
6. Open the Space URL and verify:

```bash
https://<your-space-url>/health
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

- `NEXT_PUBLIC_API_BASE_URL` = `https://<your-space-url>`

5. Deploy.

## 4) Verify End-to-End

1. Open Vercel URL.
2. Run a backtest from the dashboard.
3. Confirm charts and metrics load from live backend.

## Notes for Free Tier

- Hugging Face Spaces may sleep when idle.
- First request after idle can be slow.
- If frontend loads before backend wakes up, retry the request once.
- Backend cache uses lightweight JSON files, so no native parquet wheels are required on the host.
