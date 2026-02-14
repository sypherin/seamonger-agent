# Seamonger Dummy-Proof Setup Guide

This guide is for business owners, not developers.
Follow each step top to bottom.

## Getting Started

### 1) Get your Shopify API keys
1. Log in to Shopify Admin.
2. Go to `Settings` -> `Apps and sales channels`.
3. Click `Develop apps`.
4. Click `Create an app` and name it `Seamonger`.
5. Open your new app, then go to `Configuration`.
6. Add Admin API access for orders (read access is required).
7. Click `Install app`.
8. Copy these two values and keep them safe:
   - `Admin API access token` -> this is your `SHOPIFY_ACCESS_TOKEN`
   - Your store domain (looks like `your-store.myshopify.com`) -> this is `SHOPIFY_STORE_DOMAIN`

### 2) Link WhatsApp through OpenClaw
1. Open your OpenClaw dashboard.
2. Connect the WhatsApp number you use for supplier chats.
3. In OpenClaw API settings, copy:
   - Base/API URL -> this is `WHATSAPP_API_URL`
   - API token -> this is `WHATSAPP_API_TOKEN`
4. In OpenClaw webhook settings, set inbound webhook URL to:
   - `http://YOUR_SERVER_IP:8000/webhooks/whatsapp`
5. Save your OpenClaw settings.

## Setup

### 1) Create your `.env` file
In the project folder, run:

```bash
cp .env.example .env
```

### 2) Fill in the values
Open `.env` and replace placeholders with real values:

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

## Running

Install dependencies first:

```bash
pip install -r requirements.txt
```

Start the app:

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### Overseer Mode (you approve stuff)
Use this mode when you want visibility and control.

1. Set `FOUNDER_PHONE` to your WhatsApp number in `.env`.
2. Start the app.
3. The system mirrors inbound/outbound supplier messages to your phone.
4. If you need an emergency stop, send `no` from your founder number.

### Full Auto Mode (hands-off)
Use this mode when you want no owner intervention.

1. Leave `FOUNDER_PHONE` empty in `.env`:
   - `FOUNDER_PHONE=`
2. Start the app.
3. The system runs without mirroring or founder override.

## How It Works (Simple)

### Fisherman Memory
The system keeps a memory of each fisherman:
- What they usually supply.
- How reliable they have been.

This helps it choose the best supplier faster over time.

### Founder Mirroring
If `FOUNDER_PHONE` is set:
- You receive copies of supplier conversations.
- You stay in control without manually running every message.
- You can send `no` to stop active outreach.

## Quick Health Check
After starting, open:

- `http://YOUR_SERVER_IP:8000/health`

You should see:

```json
{"status":"ok"}
```

## Daily Use
1. Keep the app running.
2. Add/update fishermen when needed (`POST /fishermen`).
3. Let the system poll unfulfilled Shopify orders automatically.
4. Optional: trigger immediate polling with `POST /poll-now`.
