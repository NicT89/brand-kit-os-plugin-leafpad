# Perplexity

Perplexity supports **custom MCP connectors**: you provide an MCP server URL and choose OAuth,
API key, or open auth.

> **Availability:** Custom connectors are for **Pro, Max, and Enterprise** subscribers, on top
> of Perplexity's prebuilt connector catalog.

## 1. Add the connectors

In Perplexity's **Settings → Connectors** (custom connector), add each server:

**Brand Kit OS**
- **MCP server URL:** `https://www.brandkitos.com/mcp`
- **Auth:** API key → header `Authorization: Bearer <your Brand Kit OS API key>`

**Leafpad**
- **MCP server URL:** `https://leafpad.io/mcp`
- **Auth:** OAuth → complete the browser sign-in when prompted.

## 2. Port the intelligence (Space instructions)

Perplexity has no rules file. Create a **Space** for brand publishing and paste the block from
[`../portable/custom-instructions.md`](../portable/custom-instructions.md) into the Space's
**custom instructions**, then use that Space when working with these connectors.

## 3. Verify

In the Space, ask: *"List my brand kits and my Leafpad organizations using the connectors."*

## Troubleshooting

- **Connector option missing** — confirm you're on Pro/Max/Enterprise; custom MCP connectors are
  not on the free tier.
- **`403` from Brand Kit OS** — host allowlist, not the key. Contact Brand Kit OS to allowlist
  Perplexity.

> Note: a public **Comet browser** MCP refers to controlling Perplexity's browser *from* another
> agent — that's unrelated to connecting these two servers *into* Perplexity, which is what this
> guide covers.
