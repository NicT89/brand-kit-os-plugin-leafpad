---
description: Health check for the plugin — verifies both MCP servers connect, lists your brand kits and Leafpad orgs, checks the sources registry, and reports a punch list before you create content.
argument-hint: (no arguments)
---

# Doctor

Run a full pre-flight check so you know everything is wired up before creating content. Use this right after install, or any time something isn't working.

## Workflow

Run each check and report a green/yellow/red status with a fix for anything not green.

0. **Setup gate**: Before running any other checks, verify the plugin has been initialized.

   Run this bash check:
   ```bash
   test -f ~/.brand-kit-os-leafpad/config.json && echo "EXISTS" || echo "MISSING"
   ```

   - If the result is `MISSING`: stop immediately. Do not run Steps 1-7. Output exactly:
     "Plugin not initialized. Run `/brand-kit-os-leafpad:setup` first. Setup takes about 2 minutes and will connect your brand kits, configure your posting schedule, and discover content sources."
   - If the result is `EXISTS`: continue to Step 1.

1. **Brand Kit OS connection** — Call `list_brand_kits`.
   - 🟢 Returns one or more kits → list their names/ids
   - 🟡 Returns empty → "Connected, but no brand kits yet. Create one at brandkitos.com."
   - 🔴 Errors → likely API key or allowlist issue. Show the error and point to README → Prerequisites.

2. **Leafpad connection** — Call `leafpad_list_organizations`.
   - 🟢 Returns one or more orgs → list them
   - 🟡 "Needs authentication" → "Complete the Leafpad OAuth sign-in in your browser, then re-run."
   - 🔴 Errors → show the error; point to the test protocol doc.

3. **Brand kit completeness** — For the active (or each) kit, call `get_brand_kit_summary` and spot-check that `expression`, `governance`, and `audience` are populated (call those getters).
   - Report any empty critical section ("Governance is empty — voice enforcement will be weaker").

4. **Leafpad readiness** — Call `leafpad_list_posts` (existing content for internal linking) and `leafpad_get_company_data` with a test question ("What does this company do?").
   - Report whether the Knowledge Base appears populated (KB-grounded drafts are much stronger).
   - Note if there are zero existing posts (internal linking will be limited until you publish a few).

5. **Sources registry** — Check for `~/.brand-kit-os-leafpad/registry.json` (or per-kit variant).
   - 🟢 Exists and validates against the schema → summarize: N trusted sources, N citation domains, cadence
   - 🟡 Missing → "No sources registry. Topic research will fall back to web search. Want me to help you create one? (see the topic-sourcing skill)"
   - 🔴 Exists but invalid JSON/schema → show the validation error.

6. **Config** — Confirm `publish_mode` is set and report its value. Confirm the BKOS API key is configured (don't print it).

7. **Plugin version check** — Compare the installed version against the latest GitHub release.
   - The current installed version of this plugin is `1.8.0`. Update this constant in lockstep with `plugin.json` on every release.
   - Fetch the latest release via WebFetch: `GET https://api.github.com/repos/NicT89/brand-kit-os-plugin-leafpad/releases/latest`
     Parse the `tag_name` field (strip a leading `v` if present for comparison).
   - 🟢 Installed version matches or exceeds latest → "Plugin is up to date (v1.8.0)"
   - 🟡 Installed is behind latest → "Plugin v1.8.0 installed: v<latest> available. Update via Settings → Capabilities → Plugins."
   - 🔴 GitHub API unreachable or returns an error → "Version check skipped: network unavailable. Installed: v1.8.0"

## Output format

```
Brand Kit OS + Leafpad — Health Check

🟢 Brand Kit OS        Connected · 2 kits (Acme, Acme Labs)
🟢 Leafpad             Connected · 1 org (acme-inc)
🟡 Brand completeness  Governance populated; personas empty
🟢 Leafpad content     14 existing posts · Knowledge Base populated
🟡 Sources registry    Not found — topic research will use web search only
🟢 Config              publish_mode=draft · API key set
🟢 Plugin version      v1.8.0 · up to date

Punch list:
1. [registry] Run setup to add trusted sources → better topic ideas. Want me to start?
2. [personas] Optional: add AI personas in Brand Kit OS for byline attribution.
3. [version] Plugin v1.8.0 installed: v<latest> available. Update via Settings → Capabilities → Plugins.

You're ready to create content. Try:
  /brand-kit-os-leafpad:plan-week
  /brand-kit-os-leafpad:publish-pipeline "your first topic" --draft
```

## Rules

1. Never print the API key or any secret
2. Run every check even if an early one fails — give the full picture in one pass
3. For every yellow/red, give a concrete next action
4. Keep it fast and read-only — `doctor` must never create, schedule, or modify anything
5. Check version last (Step 7); it should never block the other checks from running.
