# ChatGPT (Developer Mode connectors)

ChatGPT can connect to **remote MCP servers** as custom connectors via **Developer Mode**. It
supports only remote HTTPS MCP servers (no local stdio), with OAuth or API-key auth.

> **Availability:** Developer Mode / full MCP connectors are a beta on paid plans (Plus, Pro,
> Team, Enterprise, Edu). Custom-connector creation may be gated by your workspace admin.

## 1. Enable Developer Mode

**Settings → Connectors → Advanced settings → Developer Mode** (toggle on). For workspaces:
**Workspace Settings → Permissions & Roles → Connected data / Create custom MCP connectors**.

## 2. Add the connectors

In **Settings → Connectors → Create**, add each server:

**Brand Kit OS**
- **URL:** `https://www.brandkitos.com/mcp`
- **Auth:** API key / custom header → `Authorization: Bearer <your Brand Kit OS API key>`

**Leafpad**
- **URL:** `https://leafpad.io/mcp`
- **Auth:** OAuth → complete the browser sign-in when prompted.

Enable both connectors in the composer (Developer Mode / connectors picker) for chats where you
want them.

## 3. Port the intelligence (instructions)

ChatGPT has no rules file. Reproduce the behavior by pasting the brand-voice + publish-pipeline
block from [`../portable/custom-instructions.md`](../portable/custom-instructions.md) into either:

- a **Custom GPT** → *Instructions*, or
- a **Project** → *Instructions*, or
- the chat's custom instructions.

## 4. Verify

Ask: *"Using the Brand Kit OS and Leafpad connectors, list my brand kits and Leafpad
organizations."*

## Troubleshooting

- **Connector won't add** — Developer Mode must be on and your plan/workspace must permit custom
  connectors. Only remote HTTPS endpoints are accepted.
- **`403` from Brand Kit OS** — host allowlist, not the key. Contact Brand Kit OS to allowlist
  ChatGPT.
- **Write actions blocked** — Developer Mode marks write tools (e.g. `leafpad_create_post`) as
  requiring confirmation; approve them per action.
