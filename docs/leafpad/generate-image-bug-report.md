# Bug report: `leafpad_generate_image` returns "Unauthorized" while every other Leafpad MCP tool works

**Reporter context:** Using the Leafpad MCP server (`https://leafpad.io/mcp`) from an MCP client (Claude Code), authenticated via OAuth 2.1. Organization: `brand-kit-os`.
**Date observed:** 2026-06-24/25.
**Severity:** High — AI feature-image generation is completely unusable via MCP, which breaks any automated blog-publishing flow that adds a feature image.

---

## 1. Summary

`leafpad_generate_image` fails **100% of the time** with an OAuth "Unauthorized" error, **even though every other Leafpad MCP tool — including write operations — succeeds in the same session with the same token.** The error tells the user to re-authenticate, but re-authentication is not the problem: authentication is demonstrably working for all other tools.

## 2. Exact error

Every call to `leafpad_generate_image` returns:

```
Error: Unauthorized. Authenticate via OAuth 2.1. Call
https://leafpad.io/mcp/.well-known/oauth-protected-resource to verify authentication.
```

Tool call shape used:

```json
{
  "tool": "leafpad_generate_image",
  "arguments": { "organization_slug": "brand-kit-os", "prompt": "<any prompt>" }
}
```

Reproduced **3+ times** across the session, with both a long descriptive prompt and a minimal one ("minimalist low-poly brand illustration, clean, single accent color, no text"). Not transient.

## 3. What works with the SAME authentication

In the same session, with the same OAuth token, all of these succeed — including writes:

| Tool | Type | Result |
|---|---|---|
| `leafpad_list_organizations` | read | ✅ |
| `leafpad_list_posts` | read | ✅ |
| `leafpad_get_post` | read | ✅ |
| `leafpad_list_tags` | read | ✅ |
| `leafpad_get_company_data` | read | ✅ |
| `leafpad_create_post` | **write** | ✅ (created drafts #1108, #1115, #1162) |
| `leafpad_update_post` | **write** | ✅ (edited #1162, incl. SEO + html_content) |
| `leafpad_add_scheduled_posts` | **write** | ✅ (scheduled #893, #909, #910) |
| `leafpad_generate_image` | write | ❌ **Unauthorized** |

So the token is valid, not expired, and carries **write** permission. `generate_image` is the only tool that rejects it.

## 4. Diagnostics performed

1. **Retried 3×** with different prompts → identical error each time (rules out a transient/timeout issue).
2. **Confirmed write scope is present** → `create_post`, `update_post`, and `add_scheduled_posts` all succeed, so this is not a missing write scope or an expired token.
3. **Fetched the OAuth Protected Resource Metadata** at `https://leafpad.io/mcp/.well-known/oauth-protected-resource`:

   ```json
   {
     "authorization_servers": ["https://leafpad.eu.scalekit.com/resources/res_120307199615436034"],
     "bearer_methods_supported": ["header"],
     "resource": "https://leafpad.io/mcp",
     "resource_documentation": "https://leafpad.io/mcp/docs",
     "scopes_supported": []
   }
   ```

   `scopes_supported` is **empty** — the resource advertises **no granular scopes**. So there is no per-tool scope the client could be failing to request: the client cannot ask for an "image" scope that isn't advertised.

## 5. Our best guesses at root cause

Because (a) the token is valid and write-capable, (b) no scopes are advertised, and (c) only this one tool fails, the cause is almost certainly **server-side**. In order of likelihood:

1. **Plan / feature entitlement (most likely).** AI image generation is probably gated behind a plan tier or feature flag the org doesn't have, and the endpoint returns a generic `401 Unauthorized` instead of a specific `403 "feature not enabled / upgrade required"`. The misleading error then sends users down the re-authentication dead-end.
2. **Token not propagated to the image pipeline.** The tool description says the image is produced by "an AI pipeline ... then stored on Leafpad's CDN." That pipeline is likely a separate downstream service. If the MCP OAuth bearer that the post endpoints accept is **not forwarded / re-validated correctly** by the image service, that service rejects the request as unauthorized — a server-side token-propagation bug.
3. **Undeclared scope requirement.** The image endpoint may require a scope that is **not** listed in `scopes_supported` (which is empty). Since OAuth consent never granted a scope the resource doesn't advertise, the endpoint rejects the call. If a scope is genuinely required, it must be advertised so clients can request it during consent.

## 6. Requested fixes / questions for the Leafpad team

1. **Confirm whether AI image generation is enabled** for org `brand-kit-os` / its plan. If it's plan-gated, return a clear, specific error (e.g. `403` with "AI image generation is not available on your plan") instead of a generic OAuth `401`.
2. **Verify token propagation:** confirm the image-generation endpoint accepts the same OAuth bearer that `create_post` / `update_post` / `add_scheduled_posts` accept. If a downstream image service re-checks auth, ensure the token is forwarded.
3. **If a scope is required, advertise it** in `scopes_supported` so MCP clients can request it during OAuth consent.
4. **Fix the error message.** Pointing users to "re-authenticate" is misleading when authentication is working for every other tool. The message should reflect the real cause (plan/feature/permission).

## 7. Secondary feature requests (lower priority)

- **No way to set a post's *featured image* via MCP.** `leafpad_create_post` / `leafpad_update_post` have no featured-image field; images can only be embedded **inline in the body** (`html_content` with an `<img>` tag). A `featured_image` field would let automated flows set the hero image properly.
- **No CDN upload tool.** Since `generate_image` is the only path to Leafpad's CDN and it's failing, there's no way to host an externally-generated image on Leafpad's CDN via MCP. A simple "upload image → returns CDN URL" tool would unblock automated publishing even without AI generation.
- **No Knowledge Base write via MCP.** KB sync currently requires a separate REST key (`/api/public/v1/knowledge-base`); an MCP tool would be cleaner.

---

*Prepared from a live MCP session: drafts #1108/#1115/#1162 created, #1162 edited, posts #893/#909/#910 scheduled — all succeeded; `leafpad_generate_image` failed every time with the OAuth error above.*
