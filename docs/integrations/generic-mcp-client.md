# Any MCP client / driving it from code

The workflow is just MCP tool calls orchestrated by an LLM. Any MCP-capable client — or your own code using an LLM SDK — can run it.

## Connect the servers

Both are standard HTTP MCP servers:

- **Brand Kit OS** — `https://www.brandkitos.com/mcp`, with header `Authorization: Bearer <BKOS_API_KEY>`
- **Leafpad** — `https://leafpad.io/mcp`, OAuth on first connect

Point your MCP client at both. After connecting, the client discovers the tool schemas automatically (12 BKOS tools + 9 Leafpad tools).

## Driving it from code

Pseudocode for a custom runner (e.g. using the Anthropic SDK with MCP, or any agent framework):

```
client = McpClient(servers=[brand_kit_os, leafpad])
model  = LLM(system_prompt = read("agents/content-generation.md"))

# 1. Load brand context
brand = client.call_many([
  "get_brand_kit_expression", "get_brand_kit_governance",
  "get_brand_kit_audience", "get_brand_kit_products", "get_brand_kit_core",
])

# 2. Research
facts = client.call("leafpad_get_company_data", { question: f"What do we know about {topic}?" })

# 3. Draft (HTML), per content-generation.md
article = model.run(inputs={ topic, brand, facts })

# 4. Citations, per citation-validator.md (uses web fetch/search + governance)
article = run_agent("citation-validator.md", article, brand.governance)

# 5. SEO + feature image
seo = run_agent("seo-optimizer.md", article, brand)
seo.feature_image = client.call("leafpad_generate_image", { prompt: seo.image_prompt })

# 6. QA gate, per quality-assurance.md
if not run_agent("quality-assurance.md", article, brand).passed: revise()

# 7. Publish
result = client.call("leafpad_create_post", {
  name: article.title, slug: article.slug, content: article.body_html,
  tags: seo.tags, seo: seo.seo, published: False, feature_image: seo.feature_image,
})
```

## Reusing the agent definitions

Each `agents/*.md` file is a complete role spec: a system prompt (the prose), the MCP tools it needs (the "tools used" table), its inputs, and a structured output format. Feed the prose as the system prompt and enforce the output format. The orchestration order is exactly what `commands/publish-pipeline.md` describes.

## The rich-article schema

The intermediate object passed between steps is defined in [`schemas/rich-article.schema.json`](../../schemas/rich-article.schema.json). Validate against it to keep your pipeline interoperable with the plugin's.

## Field mapping

How brand data maps to Leafpad fields is documented in [`plugins/brand-kit-os-leafpad/references/brand-to-leafpad-mapping.md`](../../plugins/brand-kit-os-leafpad/references/brand-to-leafpad-mapping.md). Remember: Leafpad's `content` is **HTML**, and it auto-derives `wordCount`/`articleSection`/`inLanguage`/FAQ schema on publish (don't send those).

## Model choice

Use a strong, recent model — the brand-compliance and citation-verification steps reward careful instruction-following and reliable tool use.
