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

1. **Check what's already connected.** Try `list_brand_kits` (Brand Kit OS) and
   `leafpad_list_organizations` (Leafpad). If both succeed, tell the user setup is already
   complete, show what each returned, and skip to step 6.
2. **Brand Kit OS API key.** If `list_brand_kits` failed because the server isn't configured, ask
   the user to paste their Brand Kit OS API key (from <https://brandkitos.com/settings> →
   API Keys; requires a Base or Premium plan). It's stored as the plugin's
   `user_config.brand_kit_api_key` (a secret) — never echo it back. If they installed via the
   marketplace, this was prompted at install; point them to re-enter it via the plugin settings
   if it's missing.
3. **Default publish mode.** Ask which default to use: `draft` (recommended — unpublished, review
   in Leafpad), `published` (live immediately), or `scheduled` (queue a topic for Leafpad to
   generate on a date). This maps to `user_config.publish_mode`.
4. **Leafpad sign-in.** Explain that the first Leafpad action opens a browser for OAuth and the
   token is cached afterward. Trigger it by calling `leafpad_list_organizations`.
5. **Verify.** Re-run `list_brand_kits` and `leafpad_list_organizations`. Report what each
   returned.
6. **Report and orient.** Summarize: active brand kit(s), Leafpad org(s), the default publish
   mode, and the three things they can do next:
   - `/brand-kit-os-leafpad:enforce-voice <request>` — on-brand content
   - `/brand-kit-os-leafpad:create-content <type | audience | topic>` — draft content
   - `/brand-kit-os-leafpad:publish-pipeline <topic | brief>` — full draft → QA → publish

## Handling failures

- **Brand Kit OS returns `403`** — the API key is valid but this client isn't allowlisted.
  Sandboxed Claude Code environments can be blocked; Claude Desktop is typically allowlisted.
  Tell the user to contact Brand Kit OS to allowlist the host. Do not treat this as a bad key.
- **No brand kits** — if `list_brand_kits` returns empty, tell the user to create a brand kit at
  <https://brandkitos.com> first.
- **Leafpad OAuth doesn't complete** — have them retry; the token caches after a successful
  sign-in.

## Rules

1. Never display or log the API key after the user provides it.
2. Don't proceed to publishing flows until both servers verify.
3. Keep it short — this is onboarding, not a tutorial. Ask only for the API key and publish mode;
   infer everything else.
