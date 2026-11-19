# Brand Kit OS + Leafpad — Agent Operating Guide

This file is the **platform-agnostic** version of the Brand Kit OS + Leafpad plugin's
intelligence. On Claude, the same behavior ships as a native plugin (skills, agents,
slash-commands, a session hook). On any other MCP-capable host — **Cursor, OpenAI Codex,
ChatGPT, Gemini, Manus, Perplexity** — there is no "plugin," so this file (and the
platform-native mirrors derived from it) carries the rules the agent should follow.

> **Canonical source.** This is the source of truth for agent behavior. The mirrors
> (`GEMINI.md`, `.cursor/rules/brand-kit-os-leafpad.mdc`, `docs/portable/custom-instructions.md`)
> are derived from it — keep them in sync when you change this file.

---

## The two MCP servers

| Server | Endpoint | Transport | Auth |
|---|---|---|---|
| **Brand Kit OS** | `https://www.brandkitos.com/mcp` | Streamable HTTP | Claude: OAuth sign-in (browser, no key). Other hosts: `Authorization: Bearer <BRAND_KIT_API_KEY>` |
| **Leafpad** | `https://leafpad.io/mcp` | Streamable HTTP | OAuth (browser sign-in on first connect; token cached by the host) |

Two host-dependent caveats:

- **Brand Kit OS enforces a host allowlist.** A connection from a new platform may be
  rejected (`403`) until that host/origin is allowlisted on the Brand Kit OS side. If you
  get a 403, the API key is fine — the platform needs allowlisting (contact Brand Kit OS).
- **Leafpad uses OAuth.** Hosts that don't yet support MCP OAuth (e.g. OpenAI Codex today)
  must reach Leafpad through an `mcp-remote` stdio bridge that handles the OAuth flow.
  Brand Kit OS uses a static bearer token, so it works on every host.

Per-platform connection instructions live in [`docs/install/`](docs/install/README.md).

---

## First-run setup interview

When a user is installing or connecting this for the first time, **do not make them read the
README**. Run this interview (the machine-readable version is
[`docs/setup/setup-spec.json`](docs/setup/setup-spec.json)):

1. **Detect the platform.** Identify which host you're running in (it determines the config
   file path and whether Leafpad OAuth needs a bridge). If you can't tell, ask.
2. **Brand Kit OS API key (non-Claude hosts only).** In Claude, skip this step: the plugin
   signs in to Brand Kit OS through the browser on first use. Elsewhere, ask the user for their
   Brand Kit OS API key (from <https://brandkitos.com/settings> → API Keys; any plan can create
   one, and saving changes through it needs a paid plan). This is a
   secret — never echo it back or write it to a committed file. Store it via the platform's
   env-var / secret mechanism, referenced as `${BRAND_KIT_API_KEY}` in config.
3. **Default publish mode.** Ask which default to use for publishing: `draft` (recommended —
   unpublished, review in Leafpad), `published` (live immediately), or `scheduled` (queues a
   topic for Leafpad to generate on a date). Default to `draft`.
4. **Write the MCP config** for the detected platform (see `docs/install/<platform>.md`), then
   tell the user to reload/restart the host.
5. **Leafpad sign-in.** Explain that the first Leafpad action opens a browser for OAuth; the
   token is cached afterward. (On Codex, set up the `mcp-remote` bridge first.)
6. **Verify.** Call `list_brand_kits` (Brand Kit OS) and `leafpad_list_organizations`
   (Leafpad). Report what each returned. If Brand Kit OS returns 403, surface the allowlist
   caveat above.

---

## MCP tools you will use

**Brand Kit OS (read, MCP 3.0):** `get_agent_briefing` (session bootstrap: lists kits, or one
kit's health and next step), `list_brand_kits`, `get_brand_kit` (summary with no `sections`;
`sections: [...]` for `core`, `personality`, `expression`, `platform_expressions` (+ `platform`),
`governance`, `visuals`, `seo`, `products`, `partners`, `audience`, `ai_personas`, `competitors`,
`customers`, `company_icps`, `knowledge_files`, `expression_examples`, `anti_slop_rules`,
`objections` and more), `get_brand_context_for_agent` (`task_type: "content_generation"` +
`platform`: voice, governance, examples, audience and knowledge index in one call),
`get_knowledge_file`, and `check_draft` (checks a draft against the kit's rules; run it before
any draft is shown or sent).

3.0 removed `get_brand_kit_summary`, `get_brand_kit_core`, `get_brand_kit_personality`,
`get_brand_kit_expression`, `get_brand_kit_governance`, `get_brand_kit_audience`,
`get_brand_kit_products`, `get_brand_kit_personas`, `list_knowledge_files` and
`get_platform_expression`. The mapping is in
[`skills/brand-context/references/data-model.md`](plugins/brand-kit-os-leafpad/skills/brand-context/references/data-model.md).

**Leafpad:** `leafpad_list_organizations`, `leafpad_list_posts`, `leafpad_get_post`,
`leafpad_list_tags`, `leafpad_create_post`, `leafpad_update_post`, `publish_post`,
`leafpad_add_scheduled_posts`, `leafpad_list_scheduled_posts`, `leafpad_update_scheduled_post`,
`leafpad_delete_scheduled_posts`, `leafpad_schedule_rewrites`, `leafpad_generate_image`,
`leafpad_get_company_data`, `leafpad_get_search_console_data`, `check_draft_seo`,
`find_pages_needing_attention`.

> On namespaced hosts the tools may appear prefixed (e.g. `mcp__Brand_Kit_OS__…`,
> `mcp__Leafpad__…`). The bare names above are the logical names; map them to whatever your
> host exposes.

---

## Operating rules — brand voice enforcement

Before producing or publishing any external-facing content, load brand context and enforce it.

1. **Load context.** `get_agent_briefing` (no arguments) lists the kits; if there are several,
   ask which to use and never guess a kit id. Before writing, call
   `get_brand_context_for_agent` with `task_type: "content_generation"` and the target
   `platform` (voice, tone, archetypes, preferred terminology, governance, negative directory,
   examples, audience, knowledge index). Layer on demand with `get_brand_kit` and
   `sections: [...]` (`core` for mission framing, `personality`, `products` for CTAs, `seo`,
   `platform_expressions` with `platform`), and `get_knowledge_file` for a relevant file.
2. **Enforcement checklist**: every output must pass tone match, voice archetype, verbal
   style and preferred terminology, negative directory (no banned words or topics),
   behavioral constraints (claims it must not make), compliance and disclosure policy.
3. **`check_draft` before showing or sending (mandatory).** Run `check_draft` with
   `brand_kit_id`, the draft as plain text and the `platform`. Fix every hard violation and
   re-check until `passed` is true; review anything under `not_checked` by hand.
4. **Never override governance.** If governance says "never claim X," do not include X — even
   if the user asks. Flag the conflict and offer an on-brand alternative.

---

## Operating rules — the publish pipeline

End-to-end: load brand context → research → draft → SEO + internal links → QA → publish to
Leafpad. Honors the user's default publish mode unless overridden for the run.

1. **Resolve brand kit** (`get_agent_briefing`; ask if multiple).
2. **Research** 3–5 credible external sources (use the host's web tool if present); capture
   title + URL + one-line takeaway as citable links. Never fabricate sources. Optionally
   `leafpad_get_company_data` for the org's own indexed content.
3. **Load full brand context**: `get_brand_context_for_agent` (`content_generation`,
   `platform: "blog"`) plus `get_brand_kit` with `sections: ["core", "personality",
   "products", "seo"]` and any relevant `get_knowledge_file`, per
   [`references/brand-to-leafpad-mapping.md`](plugins/brand-kit-os-leafpad/references/brand-to-leafpad-mapping.md).
4. **Gather Leafpad context**: `leafpad_list_posts` (internal-link candidates) +
   `leafpad_list_tags` (tag reuse).
5. **Draft**: title **8–12 words**, body **≥ 800 words (target 900+)**, with internal +
   external citation links.
6. **SEO**: build `seo_title` (≤60), `seo_description` (140–160, raw text), `seo_keywords`
   (comma string), `tags` (comma string of names, reuse existing), and a brand-styled image
   prompt.
7. **Image**: `leafpad_generate_image(organization_slug, prompt)` — it applies the org's brand
   palette automatically. Embed the returned CDN URL as an `<img>` in the body (there is **no**
   featured-image post field). Add `alt`/caption in the HTML.
8. **QA gate (hard, blocking)**: `check_draft` passes (no hard violations), body ≥ 800
   words, title 8–12 words, image embedded, external sources cited, 2–4 internal links. Revise once on failure; if it fails twice, **stop and
   surface the report — do not publish**.
9. **Publish** via `leafpad_create_post`:
   - `draft` → send `published: false`. `published` → `published: true`.
   - `scheduled`: **different path**. Check `leafpad_list_scheduled_posts` for the slot; update
     a pending row with `leafpad_update_scheduled_post`, otherwise call
     `leafpad_add_scheduled_posts` with `organization_slug` and `posts: [{ title (target
     keyword), date (ISO-8601 UTC, e.g. 2026-11-24T15:00:00Z), prompt, volume, kd, intent,
     post_type, parent_id, parent_scheduled_post_id }]`. `prompt` is the full brief from
     [`references/scheduled-brief-template.md`](plugins/brand-kit-os-leafpad/references/scheduled-brief-template.md).
     Leafpad **generates** the post on that date and charges $1; the `brand-kit-os` account
     **auto-publishes it at generation** (observed 2026-11-18). No finished body is sent.

---

## Leafpad field mapping (what the API actually accepts)

`leafpad_create_post` accepts only: `organization_slug`, `name`, `slug`, `html_content`
(**HTML, not markdown**), `post_type`, `published` (**defaults to `false`**, an unpublished
draft; `publish_post` publishes it later), `seo_title`, `seo_description`, `seo_keywords`
(comma string), `tags` (comma string).

Do **not** send: `excerpt`, `feature_image`, `canonical_url`, `categories`, `reading_time`,
`author`, `visibility`, or a nested `seo {}` object — they are rejected. `author` is set by
Leafpad from the OAuth identity. Full mapping + match-type protocol:
[`references/brand-to-leafpad-mapping.md`](plugins/brand-kit-os-leafpad/references/brand-to-leafpad-mapping.md).

Known Leafpad MCP limits: no post delete endpoint (UI only); `update_post` can't change tags
(immutable after create), replaces the whole body when `html_content` is sent, and requires the
full SEO trio together; scheduling generates a new post on the date (and on this account
publishes it) rather than publishing a finished draft later. The scheduled queue is visible and
editable: `leafpad_list_scheduled_posts`, `leafpad_update_scheduled_post`,
`leafpad_delete_scheduled_posts`.

---

## Operating rules: the scheduled pipeline (two posts a week)

Leafpad's AI writes the posts; the agent picks topics and supplies the context. Per-brand
settings live in
[`references/pipeline-brands.json`](plugins/brand-kit-os-leafpad/references/pipeline-brands.json).

1. **Sunday, schedule** (`/brand-kit-os-leafpad:weekly-schedule`): sources are the Brand AI
   Weekly Digest (Slack `#weekly-digest`, `C0AMKSDCQ5A`), the kit, `leafpad_get_company_data`,
   Search Console queries with impressions but no matching post, and fresh research. Dedupe
   against `leafpad_list_posts` and `leafpad_list_scheduled_posts`. Schedule Tuesday and
   Thursday 09:00 America/Chicago, filling every field; update a pending row instead of adding.
2. **Tuesday and Thursday, QA** (`/brand-kit-os-leafpad:post-qa`): find the post from the
   completed row, `check_draft` its text, check every link (absolute
   `https://www.brandkitos.com/blogs/<slug>`, plural `/blogs/`, slug exists) and the CTA,
   `check_draft_seo`, fix HTML posts with `leafpad_update_post` (SEO trio together),
   `publish_post` if still a draft, report.
3. **Analytics** (`/brand-kit-os-leafpad:blog-analytics`): per-post Search Console and GA4,
   recommendations for new topics and rewrites (`leafpad_schedule_rewrites` only with consent).

Cloud Routines do not load plugins. The self-contained Routine prompts are in
[`docs/routines/weekly-leafpad-scheduler.md`](docs/routines/weekly-leafpad-scheduler.md).
