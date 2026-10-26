# LUNA Studio go-live checklist

## Website
- [ ] GitHub Pages deployment succeeds for `main`.
- [ ] Open the public site on desktop and mobile; test all tabs and local video preview.
- [ ] Configure the API base URL under Backend Setup.

## Backend (Render Blueprint)
- [ ] Create a Render Blueprint from this repository using `render.yaml`.
- [ ] Add `OPENAI_API_KEY` in Render's secret environment settings only. Never commit it or place it in the website.
- [ ] Set `ALLOWED_ORIGINS=https://odusomiminwa-wq.github.io`.
- [ ] Confirm the deploy succeeds and `/health` returns `status: ok` and `ai_configured: true`.
- [ ] Upload a permitted sample video under 80 MB and verify `POST /api/analyze` returns valid JSON.
- [ ] Test missing key, invalid file, oversized upload, provider timeout, and malformed provider response.
- [ ] Save the deployed API URL in the website.

## Integrations
- [ ] Reauthorize the intended Instagram professional account and verify its username with the profile endpoint.
- [ ] Authorize the intended TikTok account and confirm the account connection is active.
- [ ] Verify the Google Drive connection can list files in the exact clip-inbox folder. A successful OAuth connection alone does not prove folder access.
- [ ] Configure a server-side worker for scheduled Drive ingestion if needed; the current website's local preview is not Drive ingestion.
- [ ] Add a legitimate trend/audio data source before claiming live trend intelligence.
- [ ] Connect supported account analytics and record only metrics returned by the platform.
- [ ] Keep all posting behind an explicit per-post approval. Never store OAuth tokens or API secrets in GitHub Pages.

## Honest capability boundaries
- AI review analyzes sampled frames and supplied notes. It does not measure real watch retention or predict virality.
- Analytics entered manually are not platform-synced.
- No post is published by this website.
