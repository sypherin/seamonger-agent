# Seamonger: Headless Agent for Seafood Procurement

Seamonger is a **headless Python agent** that works for you in the background.
It watches Shopify orders, messages fishermen on WhatsApp, tracks responses, and keeps running without a UI.

## What This Is (In Plain English)
- It is a **Python background service**, not a click-around app.
- You start it once and **keep it running**.
- While it runs, it continuously monitors unfulfilled Shopify orders and handles supplier outreach.

## How It Runs
Seamonger runs as a FastAPI app with an internal background loop.

- API process: serves endpoints like `/health`, `/webhooks/whatsapp`, `/poll-now`.
- Background worker: continuously polls Shopify for unfulfilled orders.
- Requirement: if the process stops, monitoring and automation stop.

This is why it should run under a process manager or on a server that stays online.

## The Database (Fisherman Memory)
Seamonger uses **SQLite** for memory.

- SQLite is just a **local file** (default: `seamonger.db`).
- You do **not** install a separate database server.
- That file stores the agent's memory: fishermen profiles, reliability, and conversation-linked state.

Think of it as the agent's notebook on disk.

## OpenClaw Dependency (Current Transport)
Right now, WhatsApp messaging is connected through the **OpenClaw Gateway**.

- Seamonger sends and receives WhatsApp messages via OpenClaw API/webhooks.
- To run this project as-is, OpenClaw must be available and configured.
- If you want to run without OpenClaw, you need to replace the WhatsApp transport layer (`src/whatsapp.py`) with another provider.

## Founder Experience (Founder Mirror)
If `FOUNDER_PHONE` is set, Founder Mirror is enabled.

- You receive real-time WhatsApp clones of supplier conversations.
- You can observe all outreach without manually operating each chat.
- You can intervene quickly (for example, sending `no` to halt active outreach flow).

This gives founder-level visibility while the headless agent does the repetitive work.

## Dummy-Proof Setup
### 1) Install Python
Install Python 3.11+ on your machine/server.

Check it:

```bash
python --version
```

### 2) Install project dependencies
From this project folder:

```bash
pip install -r requirements.txt
```

### 3) Configure environment variables
Create env file:

```bash
cp .env.example .env
```

Edit `.env` and set at least:

```env
SHOPIFY_STORE_DOMAIN=your-store.myshopify.com
SHOPIFY_ACCESS_TOKEN=shpat_xxx
SHOPIFY_API_VERSION=2025-10

POLL_INTERVAL_SECONDS=300

WHATSAPP_API_URL=https://your-openclaw-api-url
WHATSAPP_API_TOKEN=your_openclaw_token

FOUNDER_PHONE=+6599999999

SQLITE_PATH=seamonger.db
```

### 4) Run the main service script
Start the headless agent:

```bash
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
```

If it is running correctly:

- `GET /health` returns `{"status":"ok"}`
- The background loop keeps polling Shopify every interval

## Minimal Daily Operations
1. Keep the process running 24/7.
2. Keep OpenClaw + Shopify credentials valid.
3. Optionally call `POST /poll-now` for immediate checks.
4. Watch Founder Mirror messages (if enabled) for full visibility.

---

If you only remember one thing: **Seamonger is a headless background worker. Keep it running, and it works for you.**
