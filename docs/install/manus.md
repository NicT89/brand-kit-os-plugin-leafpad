# Manus

Manus treats custom MCP servers as integrations alongside its built-in connectors. You add each
remote server in the UI; once verified, its tools appear when building automations and agents.

## 1. Add the MCP servers

In Manus: **Settings → Integrations → Custom MCP Servers → Add**. Add each server:

**Brand Kit OS**
- **Server URL:** `https://www.brandkitos.com/mcp`
- **Auth:** API key / header → `Authorization: Bearer <your Brand Kit OS API key>`

**Leafpad**
- **Server URL:** `https://leafpad.io/mcp`
- **Auth:** OAuth → complete the browser sign-in when prompted.

After each server is verified, its tools (`list_brand_kits`, `leafpad_create_post`, …) become
available to Manus agents and automations.

## 2. Port the intelligence (instructions / knowledge)

Manus has no rules file. Reproduce the behavior by adding the block from
[`../portable/custom-instructions.md`](../portable/custom-instructions.md) to the agent's
**instructions** (or as a knowledge entry the agent always loads) so it enforces brand voice and
follows the publish pipeline.

## 3. Verify

Ask the Manus agent: *"List my brand kits and my Leafpad organizations using the custom MCP
servers."*

## Troubleshooting

- **Tools don't appear** — re-check the server shows *verified* under Custom MCP Servers, and the
  integration is enabled for the agent/automation.
- **`403` from Brand Kit OS** — host allowlist, not the key. Contact Brand Kit OS to allowlist
  Manus.

> Manus's exact auth fields and menu labels can shift as the product evolves — if the wording
> differs, look for "Custom MCP", "Server URL", and an API-key/OAuth choice.
