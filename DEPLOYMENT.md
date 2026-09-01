# Deploying CivicShield Backend to Render

## 1. The one thing that will actually bite you: RAM

Your pipeline lazily loads **four transformer models** into memory the first
time each is used:
- `cardiffnlp/twitter-roberta-base-sentiment-latest` (sentiment)
- `bhadresh-savani/bert-base-uncased-emotion` (emotion)
- `cardiffnlp/twitter-roberta-base-irony` (sarcasm)
- `jy46604790/Fake-News-Bert-Detect` (misinformation risk)

Each RoBERTa/BERT-base model is roughly 400-500MB resident in memory once
loaded. Running all four at once needs **~1.5-2GB of RAM**, comfortably.

Render's **Free** and **Starter** instance types both cap out at **512MB
RAM**. On those tiers, the process will very likely be OOM-killed the first
time `/api/v1/analytics/run-pipeline` actually runs all four models. This
isn't a hackathon inconvenience — it will just crash silently and you'll be
debugging it live in front of judges.

**Recommendation:** use the **Standard** plan (2GB RAM) for your demo
deployment. It costs money, but only for the days you actually run it —
spin it down/delete it after your judging window if budget matters. Check
Render's current pricing page for exact numbers, since these change.

If you want to stay on a free/cheap tier instead, the honest options are:
- Only load 1-2 models depending on which endpoint is hit (bigger code change)
- Swap to smaller distilled models (`distilbert`-based variants exist for
  sentiment/emotion) at some accuracy cost
- Run NLP inference as a separate scheduled batch job on a bigger box and
  keep the always-on web service lightweight (bigger architecture change)

None of these are required to get a working demo — just know which trade-off
you're making.

## 2. Deploy steps

**Option A — Blueprint (recommended, reproducible):**
1. Push this repo to GitHub.
2. In Render: New → Blueprint → connect your repo. Render will read
   `render.yaml` and provision both the web service and the Postgres
   database automatically.
3. Open `render.yaml` first and change `plan: starter` to `plan: standard`
   for the web service if you want the safer RAM headroom described above.

**Option B — Manual:**
1. New → PostgreSQL. Note the **Internal Database URL** it gives you.
2. New → Web Service → connect your repo.
   - Build command:
     ```
     pip install torch --index-url https://download.pytorch.org/whl/cpu && pip install -r requirements.txt
     ```
     (Installing the CPU-only PyTorch wheel this way avoids pulling ~2GB of
     unused CUDA libraries, which matters for Render's build-minute limits.)
   - Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Health check path: `/health`
   - Environment variable `DATABASE_URL` = the Internal Database URL from step 1
   - Environment variable `CORS_ORIGINS` = your frontend's deployed URL
     (e.g. `https://civicshield.vercel.app`) — leave as `*` only for early testing

## 3. Create the tables once

After the first successful deploy, open a Render **Shell** on the web
service and run:
```
python scripts/init_db.py
```
This only needs to run once (it's additive — safe to re-run if you add new
models later, since `Base.metadata.create_all` skips existing tables).

## 4. Connecting your frontend

- Your API base URL will be `https://<your-service-name>.onrender.com/api/v1`
- Interactive docs live at `https://<your-service-name>.onrender.com/docs` —
  useful for your frontend teammate to see exact request/response shapes
  without reading backend code.
- Set `CORS_ORIGINS` (see above) to your actual frontend origin once deployed,
  not `*` — this is a one-line env var change, not a code change.

## 5. Two things worth knowing before demo day

- **Free Postgres expires after 30 days.** Fine for a hackathon timeline,
  but if there's a gap between building and presenting, check the
  expiry date in the Render dashboard.
- **Free/Starter web services spin down after 15 minutes idle** and cold-start
  (~30-60s) on the next request. If your demo has a live judging slot, hit
  the health-check URL a minute or two beforehand to warm it up — or use a
  paid always-on plan for that window.
