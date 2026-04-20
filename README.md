# Brand Kit OS + Leafpad Plugin for Claude

Connect your brand context and Leafpad blog publishing to Claude via Model Context Protocol (MCP).

## What's included

- **2 MCP servers** — Brand Kit OS (brand context) + Leafpad (blog publishing)
- **2 skills** — Brand Context loading + Voice Enforcement
- **5 agents** — Content generation, brand review, audience adaptation, QA, and Cowork digest-to-Leafpad publisher
- **2 commands** — `/brand-kit-os-leafpad:enforce-voice` and `/brand-kit-os-leafpad:create-content`
- **Session hook** — auto-loads your brand summary at session start

## Prerequisites

1. A Brand Kit OS account with a **Base or Premium** plan
2. An API key from [Settings → API Keys](https://brandkitos.com/settings)
3. Claude Desktop with Cowork mode, or Claude Code

## Install

### From marketplace

1. In Claude, run:
   ```
   /plugin marketplace add https://github.com/NicT89/brand-kit-os-plugin-leafpad
   ```
2. Install the plugin:
   ```
   /plugin install brand-kit-os-leafpad@brand-kit-os-leafpad
   ```
3. When prompted, paste your Brand Kit OS API key.
4. Restart Claude. Ask "What brands do I have?" to verify.

### Manual install

Download the `plugins/brand-kit-os-leafpad` folder and upload it via Cowork → Customize → Browse plugins → Upload plugin.

## Leafpad blog publishing

The `cowork-digest-publisher` agent turns Cowork news digests into brand-aligned blog posts on Leafpad. It:

1. Selects the most brand-relevant topic from the digest
2. Loads brand voice, governance, and audience from Brand Kit OS
3. Gathers existing Leafpad posts for internal linking and tag reuse
4. Writes, validates (meta desc, word count, tags, links), and publishes as draft

To use it: paste a Cowork digest and ask Claude to publish it.

## Available MCP tools

### Brand Kit OS (12 tools)

| Tool | Description |
|------|-------------|
| `list_brand_kits` | List all brand kits you own or have access to |
| `get_brand_kit_summary` | Compact brand overview (~500 tokens) |
| `get_brand_kit` | Complete brand kit with all sections |
| `get_brand_kit_core` | Mission, vision, brand story, promises |
| `get_brand_kit_personality` | Traits, values, principles, moods |
| `get_brand_kit_expression` | Tone, verbal style, voice archetypes, visual style |
| `get_brand_kit_products` | Products, services, features, differentiators |
| `get_brand_kit_audience` | Target audience personas |
| `get_brand_kit_governance` | Constraints, compliance, disclosure policy |
| `get_brand_kit_personas` | AI persona configurations |
| `list_knowledge_files` | Knowledge files attached to a brand kit |
| `get_knowledge_file` | Specific knowledge file metadata |

### Leafpad (8 tools)

| Tool | Description |
|------|-------------|
| `leafpad_create_post` | Create a blog post (draft or published) |
| `leafpad_update_post` | Update an existing post (cannot update tags) |
| `leafpad_list_posts` | List existing posts for internal linking |
| `leafpad_get_post` | Read a specific post's content |
| `leafpad_list_tags` | Get existing tags for reuse |
| `leafpad_list_organizations` | List available organizations |
| `leafpad_get_company_data` | Query company knowledge base |
| `leafpad_add_scheduled_posts` | Schedule posts for future generation |

## Known Leafpad MCP limitations

- Tags return `[]` in API responses — verify in Leafpad UI
- Feature images may auto-generate; flag as manual step
- No delete endpoint — mistakes require Leafpad UI cleanup
- `leafpad_update_post` cannot modify tags after creation

## License

MIT
