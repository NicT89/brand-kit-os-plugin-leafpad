# Claude Desktop Test Protocol — v1.4.0

End-to-end test script for the Brand Kit OS + Leafpad plugin, designed to run in **Claude Desktop Chat** with both MCP servers configured. Output captured here drives the v1.5.0 calibration (which Leafpad fields are accepted vs stripped, exact scheduled timestamp format, BKOS section payload shapes).

> **Why Desktop, not Claude Code?** Both MCP servers are deployment-restricted: BKOS enforces a host allowlist (sandboxed Claude Code clients are blocked with `403 Host not in allowlist`), and Leafpad requires browser-based OAuth. Claude Desktop on your machine is on the allowlist and can complete OAuth.

## Pre-flight — configure both MCP servers

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows). If you already have a config, merge into the existing `mcpServers` block.

```json
{
  "mcpServers": {
    "brand-kit-os": {
      "url": "https://www.brandkitos.com/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_BKOS_API_KEY_HERE"
      }
    },
    "leafpad": {
      "url": "https://leafpad.io/mcp"
    }
  }
}
```

Replace `YOUR_BKOS_API_KEY_HERE` with your real key. Save. **Fully quit and reopen Claude Desktop** (Cmd-Q on macOS — not just close the window).

> **Transport note.** Both servers use direct HTTP MCP transport — no `mcp-remote` stdio proxy needed. Claude Desktop's MCP runtime handles the connection (and Leafpad's OAuth handshake) natively.

On first use of the Leafpad MCP, your browser will open for OAuth. Log in, approve, return to Claude Desktop. The token is cached by Claude Desktop.

## Path A — if you've installed the plugin via Cowork

Skip to "Phase 5: Pipeline runs." The plugin handles Phases 1-4 automatically through its agents.

## Path B — direct MCP (no plugin install in Desktop)

Use this if the plugin isn't installed in your Desktop session. Each phase below is a prompt to paste into Claude.

---

### Phase 1 — verify connections

Paste, one at a time:

```
1. List my brand kits using the brand-kit-os MCP server. Show the raw response.
```

```
2. List my Leafpad organizations using the leafpad MCP. Show the raw response.
   (First use triggers OAuth — complete in browser, then re-run if needed.)
```

**Capture:** The brand kit IDs and Leafpad org IDs from the responses. You'll reference them later.

---

### Phase 2 — schema discovery (highest-value capture)

For each Leafpad tool below, paste the prompt and copy Claude's reply into your output bundle.

```
3. Show me the FULL input schema for the leafpad_create_post MCP tool — every
   field including optional ones, with types, enum values, length/format
   constraints, and whether each is required. Print as a structured table.
```

Repeat for:

- `leafpad_add_scheduled_posts`
- `leafpad_update_post`
- `leafpad_get_post`
- `leafpad_list_posts`
- `leafpad_list_tags`
- `leafpad_list_organizations`
- `leafpad_get_company_data`

Then for BKOS:

```
4. For each Brand Kit OS tool (get_brand_kit_core, get_brand_kit_personality,
   get_brand_kit_expression, get_brand_kit_products, get_brand_kit_audience,
   get_brand_kit_governance, get_brand_kit_personas, get_brand_kit_summary),
   show me the RESPONSE schema — every nested field with its type, marked
   required vs optional. Structured table per tool.
```

> The Leafpad schemas are the single biggest unknown. Capturing them lets v1.5.0 stop guessing — strip-on-reject becomes a fallback path rather than the primary mechanism.

---

### Phase 3 — sample data pull

```
5. Get the full summary for the "Brand Kit OS" brand kit. Then call
   get_brand_kit_expression, get_brand_kit_governance, get_brand_kit_audience,
   get_brand_kit_products, get_brand_kit_personas, and get_brand_kit_personality
   for the same kit. Show each raw response in a separate code block, labeled.
```

```
6. List the knowledge files attached to the Brand Kit OS brand kit. If any,
   call get_knowledge_file for each and show the response.
```

**Capture:** The full payload bundle. We use this to verify our content-generation agent's brand-context prompts match reality.

---

### Phase 4 — manual pipeline (skip if Path A)

Walks Claude through what `/publish-pipeline` would do, without the plugin.

```
7. I want to draft a blog post for the Brand Kit OS brand kit.
   Topic: "How to choose the right voice archetype for a B2B SaaS brand"
   Steps:
   a. Use the brand kit data you already pulled (expression, governance,
      audience, products) — don't re-fetch.
   b. Use leafpad_list_posts to find 2-4 existing posts that could be linked
      internally.
   c. Use leafpad_list_tags to find tags I can reuse.
   d. Draft an 800-1200 word blog post following the brand voice.
   e. Build SEO metadata: title (≤60 chars), description (140-160 chars),
      keywords (4-8), excerpt (160-240 chars distinct from description).
   f. Suggest a feature image prompt aligned with the brand visual style.
   g. Run the brand voice enforcement checklist against the draft and report
      any violations.
   Return the complete rich-article object (title, slug, body, excerpt, tags,
   categories, seo, feature_image, internal_links, reading_time) plus brand
   application notes (voice, tone, terminology, governance, audience persona,
   products referenced).
```

---

### Phase 5 — draft publish

```
8. Take the rich-article object from the previous step and call leafpad_create_post
   with EVERY field populated — name, slug, content, tags, seo, published=false,
   excerpt, feature_image, og_image, categories, content_format="markdown",
   reading_time, author_name (if applicable). For any field Leafpad rejects with
   "unknown field" / "unexpected property" / similar, remove it and retry. Keep
   retrying up to 3 times, stripping one field per retry.

   When done, report a structured table:
   - accepted: fields Leafpad saved
   - stripped: fields Leafpad rejected (with the exact error message for each)
   - auto_generated: fields where the saved value differs from what we sent
     (especially feature_image — Leafpad may auto-generate)
   - the resulting Leafpad post URL
   - the post_id
```

**Capture:** the entire schema-fit table. This is the single most valuable artifact for v1.5.0.

---

### Phase 6 — scheduled publish

```
9. Now schedule a SECOND draft for 2026-06-15T13:00:00Z. Same rich-article
   object shape, but for a different topic of your choosing relevant to the
   brand. Use leafpad_add_scheduled_posts. Report:
   - which scheduled_at format the tool accepted (ISO 8601? Unix epoch?
     What timezone interpretation?)
   - the full tool response
   - the schema-fit table (same as Phase 5)
```

**Capture:** the exact scheduled_at format the API accepted. Our publisher needs to match.

---

### Phase 7 — low-fit topic (calibration)

```
10. Attempt a draft for an off-brand topic: "Best practices for
    cryptocurrency arbitrage trading." Use the brand kit data to score
    relevance. If the topic doesn't fit, say so and STOP — don't write.
    Report your relevance reasoning.
```

**Capture:** whether the brand-fit gating works correctly. If Claude writes the off-brand article anyway, our enforcement checklist needs strengthening.

---

## Output bundle — paste back to me

Wrap your results in this template and paste in our chat:

```
=== PHASE 1 — connections ===
brand kits: [list]
leafpad orgs: [list]

=== PHASE 2 — schemas ===
leafpad_create_post: [table]
leafpad_add_scheduled_posts: [table]
leafpad_update_post: [table]
leafpad_get_post: [table]
leafpad_list_posts: [table]
leafpad_list_tags: [table or "returned []"]
leafpad_list_organizations: [table]
leafpad_get_company_data: [table]

get_brand_kit_core: [table]
get_brand_kit_personality: [table]
get_brand_kit_expression: [table]
get_brand_kit_products: [table]
get_brand_kit_audience: [table]
get_brand_kit_governance: [table]
get_brand_kit_personas: [table]
get_brand_kit_summary: [table]

=== PHASE 3 — sample BKOS data ===
(paste raw responses)

=== PHASE 5 — draft schema_fit ===
accepted: [...]
stripped: [{ field, error }]
auto_generated: [...]
url: ...
post_id: ...

=== PHASE 6 — scheduled schema_fit ===
accepted: [...]
stripped: [{ field, error }]
scheduled_at format accepted: ...
url / post_id: ...

=== PHASE 7 — low-fit calibration ===
did Claude refuse? yes/no
reasoning Claude gave: ...
```

## What I'll do with the output

1. Update `references/brand-to-leafpad-mapping.md` — move "candidate" fields that Leafpad accepted into "verified"; move rejected ones into a new "unsupported" section.
2. Hard-code the verified `scheduled_at` format in `leafpad-publisher`.
3. Calibrate `seo-optimizer`'s defaults using the real BKOS payload shapes.
4. Adjust the brand-fit threshold based on Phase 7 behavior.
5. Open the v1.5.0 PR (topic-scout, citation-validator, /plan-week, /execute-calendar, /doctor, portable prompts/) with everything tuned to your real data.

## Troubleshooting

- **BKOS returns 403 / Host not in allowlist** — your machine isn't on BKOS's allowlist. Contact Brand Kit OS support.
- **Leafpad OAuth loops** — quit Claude Desktop fully, reopen, and try again. If still looping, check Claude Desktop's MCP logs for the auth handshake error.
- **Server shows as disconnected after config edit** — make sure you fully quit Claude Desktop (Cmd-Q on macOS) before reopening. Just closing the window doesn't reload the MCP config.
- **Schema returned is empty / Claude says it doesn't know** — the MCP server may not advertise its schema. Ask Claude to call the tool with a minimal payload and report the validation error; that surfaces required fields by elimination.
