# LUNA Studio API backend

This repository now includes a FastAPI backend for sampled-frame AI video review.

## Features
- `GET /health` readiness check.
- `POST /api/analyze` accepts a video plus platform, goal, hook notes, payoff notes and draft caption.
- Validates upload size (80 MB), extracts five representative frames with FFmpeg, and requests a structured creative review from the OpenAI Responses API.
- Returns scores, verdict, strengths, fixes, hook ideas, caption suggestion, SEO keywords and hashtags.
- CORS is restricted to the configured website origin by default.
- Temporary files are deleted after each request. The backend does not publish to social accounts.

## Deploy the API
1. Create a service on Render from this GitHub repository and select the included `render.yaml` Blueprint, or create a Docker web service with Dockerfile path `./backend/Dockerfile` and Docker context `./backend`.
2. In the hosting provider's secret/environment settings, add `OPENAI_API_KEY` with your own API key. Never put the key in `index.html`, a public repository, or the browser.
3. Keep `OPENAI_MODEL` as `gpt-4.1-mini` unless you intentionally change it.
4. Set `ALLOWED_ORIGINS` to the exact public website origin, e.g. `https://odusomiminwa-wq.github.io` (no trailing slash).
5. Wait for deployment and verify `https://YOUR-API-HOST/health` returns JSON with `status: ok` and `ai_configured: true`.
6. Open the LUNA Studio website, paste the API's base URL into **AI backend URL**, select a video, then choose **Run AI video review**.

## Run locally
Requires Python 3.12+ and FFmpeg (including ffprobe) installed on your machine.

```bash
cd backend
python -m venv .venv
# activate the environment, then:
pip install -r requirements.txt
export OPENAI_API_KEY="your-key"
uvicorn main:app --reload --port 8000
```

Open `http://localhost:8000/docs` to inspect the API. Do not commit real API keys.

## Important limitations
- The review samples frames; it does not truly understand every moment of video motion or measure TikTok/Instagram retention.
- Actual retention, average watch time, shares and follows must come from platform analytics and are not fabricated by this API.
- This service is not connected to social account publishing.
- Hosting providers may sleep free instances or impose limits; video review may take a minute or more.
- Do not upload private or sensitive footage. Use only assets you are allowed to process.
