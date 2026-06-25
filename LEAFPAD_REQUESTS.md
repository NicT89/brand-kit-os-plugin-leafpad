# Leafpad MCP feature requests

Gaps discovered while building this plugin. Each unlocks specific functionality in the BKOS+Leafpad workflow. Captured here so we can surface them with Leafpad's team.

## Bugs (blocking)

### 0. `leafpad_generate_image` returns `Unauthorized` (server-side)

**Symptom:** every call returns `Error: Unauthorized. Authenticate via OAuth 2.1`, 100% of the time, while **every other Leafpad tool — including writes** (`create_post`, `update_post`, `add_scheduled_posts`) — succeeds with the same OAuth token in the same session.

**Evidence it isn't client auth:** the OAuth Protected Resource metadata advertises `scopes_supported: []` (no per-tool scope to be missing), and all read + write tools authenticate fine. So it's a **Leafpad-side issue** — most likely a plan/feature entitlement for AI image generation (returning a generic 401 instead of a clear 403), or the OAuth bearer not being propagated to the downstream image pipeline.

**Asks:** confirm image-gen is enabled for the org/plan; verify the image endpoint accepts the same bearer the post endpoints accept; advertise any required scope; fix the misleading "re-authenticate" error message. (A full written report has been shared with the Leafpad team.)

**Workaround:** generate the image with Gamma/Higgsfield and embed the URL inline; hot-links a non-Leafpad CDN until this is fixed.

### 0b. Featured-image field + CDN image-upload

**Why:** `leafpad_create_post` / `leafpad_update_post` have **no featured-image field** — images can only be embedded inline in `html_content`. And with `generate_image` down, there's **no way to host an externally-generated image on Leafpad's CDN** via MCP.

**Shape:** add a `featured_image` field on create/update, and a `leafpad_upload_image({ org_id, file_url | bytes }) -> cdn_url` tool.

## High-priority — would unlock specific workflows

### 1. `publish_at` field on `leafpad_update_post`

**Why:** Today, a user can write a perfectly brand-aligned draft via `/publish-pipeline --draft` but cannot schedule it to flip live at a specific future time. `leafpad_add_scheduled_posts` is for AI-generated posts (different workflow). Without `publish_at`, the user must remember to manually publish at the target time.

**Shape:** `leafpad_update_post({ post_id, published: true, publish_at: "2026-06-15T13:00:00Z" })`

### 2. Knowledge Base push via MCP

**Why:** Leafpad's KB is the integration hook for BKOS — pushing brand voice, audience, governance, and product context into the KB makes every Leafpad-AI-generated post (via `leafpad_add_scheduled_posts`) brand-aware. The REST endpoint at `POST /api/public/v1/knowledge-base` works, but exposing it as an MCP tool would let a Claude conversation push BKOS data in-flow.

**Shape:** `leafpad_kb_upload({ org_id, content?: string, file_url?: string, title, tags? })`

### 3. Writing Style read/write via MCP

**Why:** BKOS owns voice/tone data. Today there's no programmatic way to push that into Leafpad's Writing Style settings, so AI-generated posts on Leafpad's side use whatever the dashboard has — potentially out of sync with BKOS. Read/write would let the plugin auto-sync.

**Shape:** `leafpad_writing_style_get({ org_id })`, `leafpad_writing_style_set({ org_id, tone, point_of_view, reading_level, post_length, structure })`

## Medium-priority — closes content management gaps

### 4. `leafpad_delete_post`

**Why:** Mistakes happen (draft committed too soon, duplicate slug, abandoned post). Today the user has to go to the Leafpad UI to clean up.

**Shape:** `leafpad_delete_post({ post_id })`

### 5. `leafpad_create_tag`

**Why:** `leafpad_list_tags` lets us read; we can attach existing tags via `leafpad_create_post`. But there's no way to programmatically create a new tag, which means new categories the brand wants to introduce require dashboard access.

**Shape:** `leafpad_create_tag({ org_id, name, slug?, description? })`

## Low-priority — observability and analytics

### 6. `leafpad_get_post_analytics`

**Why:** Closes the loop on "what's working." Without analytics, the publish pipeline can't learn from past performance to refine topic selection. Leafpad's analytics is on their roadmap; whenever it ships, an MCP read tool would unlock data-driven topic selection in v1.6+.

**Shape:** `leafpad_get_post_analytics({ post_id, range? })` returning `{ views, avg_time, scroll_depth, conversions? }`

### 7. Post-type support

**Why:** `leafpad_list_posts` returns `type: "ARTICLE"` on every post. No documentation on whether docs, changelog, landing pages, or other types are supported via MCP. Confirmation either way (and tool support if they exist) would let the plugin handle the full Leafpad surface area.

## Plugin-side workarounds (until vendor support)

- **Scheduled hand-crafted publish (#1)** — Plugin creates a draft and surfaces a manual-publish reminder. v1.6 may add a Cowork scheduled-session helper that flips published at a target time.
- **KB push (#2)** — v1.6 will add a `/sync-brand-to-kb` command using the REST endpoint until an MCP tool ships.
- **Writing Style sync (#3)** — Same v1.6 command, via REST if available.
- **Delete (#4)** — User goes to Leafpad UI; documented as a known limitation.
- **Tag creation (#5)** — Tags supplied to `leafpad_create_post` appear to be created if they don't exist (needs confirmation on the Phase 5 test). If not, document the dashboard workaround.
