---
description: Guided first-run setup — connect Brand Kit OS + Leafpad, set your default publish mode, and verify the connection.
argument-hint: (no arguments — runs the setup interview)
---

# Setup

Walk the user through connecting the Brand Kit OS + Leafpad plugin without making them read the
README. Follow the machine-readable interview in
[`../../../docs/setup/setup-spec.json`](../../../docs/setup/setup-spec.json). On other hosts the
same interview is carried by `AGENTS.md` / `GEMINI.md` / the Cursor rule; here on Claude, run it
conversationally.

## Workflow

Setup must be run before any other plugin command. It is safe to re-run at any time: it is idempotent and will never overwrite values the user has already customized.

1. **MCP gate**: Verify both required MCPs are reachable before doing any work.

   Run two checks in parallel:
   - Call `list_brand_kits` (Brand Kit OS MCP). If it errors or returns empty, output: "Brand Kit OS MCP is not connected. Enable it in your Claude MCP settings at brandkitos.com, then re-run /setup."
   - Call `leafpad_list_organizations` (Leafpad MCP). If it errors, output: "Leafpad MCP is not connected. Enable it in your Leafpad account settings, then re-run /setup."

   If either check fails, stop. Do not proceed to Step 2.

2. **Select active brand kit**: Call `list_brand_kits`. If only one brand kit exists, select it automatically and tell the user. If multiple exist, show a numbered list and ask the user to choose. Store the selection as `active_brand_kit_id` and `active_brand_kit_slug` (use the slug from the brand kit name, lowercased with hyphens).

3. **Select active Leafpad organization**: Call `leafpad_list_organizations`. If only one org exists, select it automatically. If multiple, ask the user to choose. Store as `active_leafpad_org`.

4. **Default publish mode**: Ask: "When content is ready, should I (1) publish immediately, (2) save as draft for your review, or (3) always ask? Default is draft." Accept the user's choice and store as `publish_mode` with values `"immediate"`, `"draft"`, or `"ask"`. Default to `"draft"` if the user presses enter without answering.

5. **Cadence selection**: Show the default posting schedule:

   > "Default schedule: 3 posts per week, Monday / Wednesday / Friday at 9:00 AM America/Chicago."

   Ask: "Does this work for you, or would you like to change the frequency, days, or time?"

   If the user confirms, write `topic_cadence` to `sources.json` with these defaults:

   ```json
   {
     "posts_per_week": 3,
     "preferred_days": ["Monday", "Wednesday", "Friday"],
     "preferred_time": "09:00",
     "timezone": "America/Chicago"
   }
   ```

   If the user wants to change it, ask for (a) number of posts per week, (b) preferred days, (c) preferred time, (d) timezone. Write their selections to `topic_cadence`. Validate that `posts_per_week` matches the number of days provided. If not, ask them to clarify.

6. **Scaffold local file structure**: Create the following directories and files if they do not already exist. Never overwrite existing files.

   Directories to create:

   ```bash
   mkdir -p ~/.brand-kit-os-leafpad/
   mkdir -p ~/.brand-kit-os-leafpad/brands/<slug>/
   mkdir -p ~/.brand-kit-os-leafpad/cache/rss/
   mkdir -p ~/.brand-kit-os-leafpad/cache/web/
   mkdir -p ~/.brand-kit-os-leafpad/logs/
   mkdir -p ~/.brand-kit-os-leafpad/calendars/
   mkdir -p ~/.brand-kit-os-leafpad/trusted_sources/
   ```

   Files to create (skip if already exists).

   `~/.brand-kit-os-leafpad/config.json`:

   ```json
   {
     "publish_mode": "<from step 4>",
     "active_brand_kit_id": "<from step 2>",
     "active_brand_kit_slug": "<from step 2>",
     "active_leafpad_org": "<from step 3>",
     "plugin_version": "1.8.0",
     "setup_completed_at": "<today's date ISO 8601>",
     "setup_completed_by": "setup-command"
   }
   ```

   `~/.brand-kit-os-leafpad/brands/<slug>/sources.json`:

   ```json
   {
     "brand_kit_id": "<from step 2>",
     "brand_kit_slug": "<from step 2>",
     "last_updated": "<today's date ISO 8601>",
     "trusted_sources": [],
     "seo_keyword_clusters": [],
     "authoritative_citations": {
       "domains": [],
       "prefer_recent": true,
       "max_age_days": 365
     },
     "competitor_content_feeds": [],
     "topic_cadence": {
       "posts_per_week": 3,
       "preferred_days": ["Monday", "Wednesday", "Friday"],
       "preferred_time": "09:00",
       "timezone": "America/Chicago"
     }
   }
   ```

   Replace `topic_cadence` with values from Step 5.

   `~/.brand-kit-os-leafpad/brands/<slug>/history.json`:

   ```json
   {
     "brand_kit_slug": "<from step 2>",
     "published": [],
     "drafted": []
   }
   ```

   Backward compatibility: if `~/.brand-kit-os-leafpad/registry.json` exists from a pre-v1.7.0 install, do not delete it. Mention it to the user and suggest they can manually migrate its `trusted_sources` into the new `brands/<slug>/sources.json`.

7. **Source discovery**: Tell the user: "Now I'll scan your Gmail for newsletters you subscribe to and set up your content sources. This is where topic ideas come from. You can also add Substack feeds, Reddit communities, your website, and competitor sites."

   Run the `discover-sources` command inline (see `commands/discover-sources.md`). Pass `brand_kit_slug` and `brand_kit_id` as context. Discovery runs interactively: the user answers a few questions.

   After discovery completes, update `sources.json` with results. If the user skips discovery, set `trusted_sources` to seeded defaults from `references/trusted-sources/default-sources.json` (see Step 8).

8. **Seed trusted sources**: After discovery, offer to seed curated sources from the plugin's built-in repository:

   "I can also add curated sources from our trusted sources library. Which categories are relevant to your brand? (Select all that apply): AI/Tech, Marketing/Brand, SaaS/Startups, AI Agents/MCP, Reddit Communities"

   Read `references/trusted-sources/default-sources.json`. For each category the user selects, add all entries from that category into `trusted_sources` in `brands/<slug>/sources.json`. Merge additively: never overwrite entries that discovery already added. Deduplicate by `rss` URL before saving.

9. **Leafpad sign-in check**: Call `leafpad_list_organizations` again. If it returns the user's org, confirm: "Leafpad is connected." If not, tell the user to sign in at leafpad.ai and re-run setup.

10. **Verify Knowledge Base**: Call `leafpad_get_company_data` for the active org. If a Knowledge Base exists, confirm it is populated. If empty, note: "Your Leafpad Knowledge Base is empty. Running /brand-kit-os-leafpad:sync-brand-to-kb will push your brand context there so every AI-generated post is brand-aware."

11. **Report and orient**: Output a summary:

    ```
    Setup complete for <brand kit name>

    Brand kit:     <name>
    Leafpad org:   <org>
    Publish mode:  <mode>
    Schedule:      <posts_per_week> posts/week, <days>, <time> <timezone>
    Sources found: <count> RSS feeds discovered

    Next steps:
    - Run /brand-kit-os-leafpad:plan-week to build this week's content calendar
    - Run /brand-kit-os-leafpad:discover-sources anytime to add more content sources
    - Run /brand-kit-os-leafpad:sync-brand-to-kb to push brand context to Leafpad
    - Run /brand-kit-os-leafpad:doctor to verify everything is healthy
    ```

## Rules

1. Never overwrite an existing file unless the user explicitly confirms.
2. Merge sources additively: never replace an existing `trusted_sources` array entry.
3. Never print API keys or secrets.
4. Both MCP connections must succeed in Step 1 before any other step runs.
5. The cadence the user sets in Step 5 must be written to `topic_cadence` in `sources.json`: it is the source of truth for all scheduling.
6. If setup is interrupted, it is safe to re-run from the beginning. Steps that find existing files skip creation gracefully.

## Handling failures

- **Brand Kit OS returns `403`**: the API key is valid but this client isn't allowlisted.
  Sandboxed Claude Code environments can be blocked; Claude Desktop is typically allowlisted.
  Tell the user to contact Brand Kit OS to allowlist the host. Do not treat this as a bad key.
- **Leafpad OAuth doesn't complete**: have them retry; the token caches after a successful
  sign-in.

## When no brand kit is found

"No brand kits found in Brand Kit OS. Create your brand kit at brandkitos.com first, then re-run /setup."
