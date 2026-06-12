---
description: Push Brand Kit OS context (voice, governance, audience, products) into your Leafpad Knowledge Base so every Leafpad-AI-generated post is brand-aware. Uses Leafpad's Knowledge Base REST API.
argument-hint: [--sections all|voice|governance|audience|products|core] [--dry-run]
---

# Sync Brand to Knowledge Base

Push your Brand Kit OS data into your Leafpad organization's Knowledge Base. This is the key integration between the two systems: once your brand context lives in Leafpad's KB, **every** AI-generated Leafpad post (including `/ai-schedule` and `/execute-calendar --ai-schedule`) draws from it automatically — not just posts the plugin hand-crafts.

> **Why this matters.** Leafpad's AI scheduler generates posts on Leafpad's side using its Writing Style + Knowledge Base. The plugin can pass a brand-aware brief per post, but syncing the full brand context into the KB makes the brand alignment persistent and applies to content generated outside the plugin too.

## Prerequisites

- A Leafpad API key with Knowledge Base write access (separate from the MCP OAuth — the KB endpoint is REST). Get it from your Leafpad dashboard.
- The plugin reads it from the `LEAFPAD_API_KEY` environment variable, or prompts you for it.

## How it works

Leafpad exposes a REST endpoint (not an MCP tool yet — see `LEAFPAD_REQUESTS.md`):

```
POST https://leafpad.io/api/public/v1/knowledge-base
Authorization: Bearer <LEAFPAD_API_KEY>
```

It accepts file uploads or raw text, with a 50 MB per-org quota and 2,000 requests/day per key. This command formats Brand Kit OS sections into clean KB documents and posts them.

## Arguments

- `--sections` — which brand sections to sync (default `all`). Options: `all`, `voice` (expression), `governance`, `audience`, `products`, `core`. Comma-separate multiples.
- `--dry-run` — assemble the documents and show what *would* be uploaded, without calling the API.

Examples:

```
/brand-kit-os-leafpad:sync-brand-to-kb
/brand-kit-os-leafpad:sync-brand-to-kb --sections voice,governance
/brand-kit-os-leafpad:sync-brand-to-kb --dry-run
```

## Workflow

1. **Resolve brand kit** — `get_brand_kit_summary`; if multiple, ask which.
2. **Resolve Leafpad org** — `leafpad_list_organizations`; if multiple, ask which org's KB to sync into.
3. **Pull brand sections** — Call the relevant BKOS getters for the requested `--sections`.
4. **Format KB documents** — Turn each section into a clean, titled Markdown document optimized for retrieval:
   - `Brand Voice & Tone` (from expression)
   - `Brand Governance & Compliance` (from governance — constraints, negative directory, disclosure)
   - `Target Audience & Personas` (from audience)
   - `Products & Differentiators` (from products)
   - `Brand Core — Mission, Vision, Promises` (from core)
   Each doc is tagged so it's easy to manage/replace later.
5. **Dry-run or upload**:
   - `--dry-run` → print each document and its target, stop.
   - otherwise → `POST` each document to the KB endpoint with the Leafpad API key. Respect the rate limit.
6. **Report** — What was synced, document sizes, KB quota used (if returned), and any errors.

## Output format

```
Brand → Leafpad KB Sync
Brand: <kit>   ·   Org: <org>   ·   Mode: live | dry-run

| Section     | Document Title                         | Size   | Status   |
|-------------|----------------------------------------|--------|----------|
| voice       | Brand Voice & Tone                     | 4.2 KB | uploaded |
| governance  | Brand Governance & Compliance          | 2.1 KB | uploaded |
| audience    | Target Audience & Personas             | 3.8 KB | uploaded |
| products    | Products & Differentiators             | 5.0 KB | uploaded |

KB quota: 15.1 KB used of 50 MB
Re-run after you update your brand kit to keep Leafpad's KB current.
```

## Rules

1. **Always offer `--dry-run` first** for a new user so they see what's uploaded before it lands
2. Never upload secrets — only brand content. The Leafpad API key is read from env/prompt, never written to the KB or to disk
3. Tag/title documents consistently so re-syncing replaces rather than duplicates (note: if Leafpad's KB has no update/replace, warn that re-syncing may create duplicates — track in `LEAFPAD_REQUESTS.md`)
4. Respect the 2,000 req/day rate limit; batch sensibly
5. Confirm the target org before uploading — KB writes affect every AI-generated post in that org

## When this isn't available

If you don't have a Leafpad REST API key, you can still upload these documents manually: run `--dry-run`, copy each document, and paste it into Leafpad → Knowledge Base in the dashboard. The brand-awareness benefit is the same.
