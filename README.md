# Seamonger Autonomous Procurement System

## Overview
An agentic procurement engine that proactively sources fish supplies based on Shopify orders by negotiating with fishermen 1-to-1 on WhatsApp.

## Core Problem
- **Supply Matching:** Identifying which individual fisherman has the specific stock required for unfulfilled Shopify orders.
- **Unstructured Negotation:** Handling voice notes and free-text dialects (Singlish/Malay).
- **Founder Oversight:** Maintaining full visibility and control for the owner.

## System Architecture
- **Input:** Shopify Order API (Unfulfilled orders).
- **Communication:** Individual WhatsApp DMs (via OpenClaw/WACLI).
- **Intelligence:** 
    - Intent Extraction for supplier replies.
    - **Fisherman Memory:** SQLite DB to learn who specializes in what and who is reliable.
- **Oversight:** Real-time mirroring of all comms to the Founder's WhatsApp with override capability.

## Roadmap (GSD Phase 1 - REDO)
- [ ] Shopify order poller.
- [ ] Fisherman database (SQLite schema).
- [ ] 1-to-1 WhatsApp dispatcher.
- [ ] Founder mirror/sync service.
- [ ] Override/Human-in-the-loop logic.
